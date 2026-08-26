"""Deterministic financial planning from explicit founder assumptions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.lifecycle import LifecycleFinancialPlan, StartupProfile
from app.models.user import User
from app.schemas.financial_plan import FinancialPlanInput


class FinancialPlanService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _profile(self, user: User, profile_id: str) -> StartupProfile:
        profile = self.session.get(StartupProfile, profile_id)
        if not profile or profile.created_by_id != user.id:
            raise ResourceNotFoundError("Startup profile was not found.")
        return profile

    def create(self, user: User, profile_id: str, payload: FinancialPlanInput) -> LifecycleFinancialPlan:
        profile = self._profile(user, profile_id)
        initial_capital = float(profile.expected_investment or profile.available_budget or 0)
        available_budget = float(profile.available_budget or 0)
        monthly_expenses = round(
            payload.monthly_rent
            + payload.monthly_salary_cost
            + payload.monthly_marketing_cost
            + payload.monthly_other_cost
            + payload.monthly_utilities_cost
            + payload.monthly_software_delivery_cost
            + payload.monthly_loan_repayment,
            2,
        )
        calculated_revenue = round(payload.expected_monthly_sales * payload.average_sale_value, 2)
        monthly_revenue = payload.expected_monthly_revenue or calculated_revenue
        gross_profit = round(monthly_revenue * (payload.gross_margin_percent / 100), 2)
        monthly_profit = round(gross_profit - monthly_expenses, 2)
        break_even_revenue = round(monthly_expenses / (payload.gross_margin_percent / 100), 2)
        runway_months = round(available_budget / monthly_expenses, 1) if monthly_expenses else None
        break_even_months = round(initial_capital / monthly_profit, 1) if initial_capital and monthly_profit > 0 else None
        annual_profit = round(monthly_profit * 12, 2)
        annual_roi = round((annual_profit / initial_capital) * 100, 1) if initial_capital else None
        upfront_cash_needed = round(payload.one_time_setup_cost + payload.emergency_fund, 2)
        break_even_units = round(break_even_revenue / payload.average_sale_value) if payload.average_sale_value > 0 else None
        assumptions = payload.model_dump() | {"initial_capital": initial_capital, "available_budget": available_budget, "monthly_revenue_used": monthly_revenue, "currency_note": "Enter values in one consistent currency, such as LKR."}
        results = {"monthly_expenses": monthly_expenses, "monthly_revenue": monthly_revenue, "gross_profit": gross_profit, "monthly_profit": monthly_profit, "annual_profit": annual_profit, "break_even_revenue": break_even_revenue, "break_even_units": break_even_units, "break_even_months": break_even_months, "runway_months": runway_months, "annual_roi_percent": annual_roi, "capital_per_partner": round(initial_capital / payload.partner_count, 2), "upfront_cash_needed": upfront_cash_needed, "cash_gap": round(max(upfront_cash_needed - available_budget, 0), 2), "status": "profitable" if monthly_profit > 0 else "loss-making", "methodology": "Revenue × gross margin − monthly expenses. Revenue uses your direct monthly estimate, or sales volume × average sale value when the direct estimate is zero."}
        plan = LifecycleFinancialPlan(startup_profile_id=profile.id, assumptions=assumptions, results=results)
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan

    def latest(self, user: User, profile_id: str) -> LifecycleFinancialPlan:
        self._profile(user, profile_id)
        plan = self.session.scalar(select(LifecycleFinancialPlan).where(LifecycleFinancialPlan.startup_profile_id == profile_id).order_by(LifecycleFinancialPlan.created_at.desc()))
        if not plan:
            raise ResourceNotFoundError("No financial plan exists for this startup profile.")
        return plan
