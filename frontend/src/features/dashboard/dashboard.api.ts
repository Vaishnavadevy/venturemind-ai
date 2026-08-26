import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'

export interface DashboardMetric { label: string; value: string; detail: string }
export interface DashboardProject { id: string; name: string; industry: string; stage: string; status: string; score: number | null; evaluation_id: string | null; updated_at: string }
export interface DashboardScore { metric: string; score: number }
export interface DashboardRisk { label: string; level: 'High' | 'Moderate' | 'Low'; score: number; detail: string }
export interface DashboardReport { id: string; name: string; project_id: string; evaluation_id: string | null; generated_at: string | null; status: string }
export interface DashboardJourney {
  profile_complete: boolean; risk_complete: boolean; financial_plan_complete: boolean; requirements_complete: boolean; profile_updated_at: string | null
  profile_id: string | null; project_name: string | null; profile_completion_percentage: number; risk_score: number | null
  monthly_profit: number | null; cash_runway_months: number | null; break_even_months: number | null
  registration_progress_percentage: number; registration_status: string | null
}
export interface DashboardSnapshot { metrics: DashboardMetric[]; projects: DashboardProject[]; latest_project: DashboardProject | null; score_breakdown: DashboardScore[]; trend: DashboardScore[]; risks: DashboardRisk[]; reports: DashboardReport[]; journey: DashboardJourney }

export const dashboardApi = {
  get: async () => (await apiClient.get<APIResponse<DashboardSnapshot>>('/dashboard')).data.data,
}
