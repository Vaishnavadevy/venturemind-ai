"""Transparent investment-planning request and response contracts."""

from pydantic import BaseModel, ConfigDict, Field


class FinancialPlanInput(BaseModel):
    partner_count: int = Field(ge=1, le=10)
    monthly_rent: float = Field(ge=0)
    monthly_salary_cost: float = Field(ge=0)
    monthly_marketing_cost: float = Field(ge=0)
    monthly_other_cost: float = Field(ge=0)
    monthly_utilities_cost: float = Field(default=0, ge=0)
    monthly_software_delivery_cost: float = Field(default=0, ge=0)
    monthly_loan_repayment: float = Field(default=0, ge=0)
    one_time_setup_cost: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    expected_monthly_sales: float = Field(default=0, ge=0)
    average_sale_value: float = Field(default=0, ge=0)
    expected_monthly_revenue: float = Field(default=0, ge=0)
    gross_margin_percent: float = Field(default=50, ge=1, le=99)


class FinancialPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    startup_profile_id: str
    assumptions: dict[str, object]
    results: dict[str, object]
