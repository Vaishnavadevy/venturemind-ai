import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'

export interface StartupProfilePayload {
  business_name: string
  category: string
  description: string
  industry: string | null
  target_customers: string | null
  country: string | null
  district: string | null
  city: string | null
  expected_investment: number | null
  available_budget: number | null
  business_experience: string | null
  business_goals: string | null
  business_size: string | null
  startup_type: string | null
  partner_count: number
  expected_employees: number
  launch_timeline: string | null
}

export interface StartupProfileResponse extends StartupProfilePayload {
  id: string
  organization_id: string
  status: string
}

export interface LifecycleMilestoneResponse {
  id: string
  milestone_key: string
  title: string
  weight: number
  completed_at: string | null
}

export interface LifecycleRiskAssessment {
  id: string
  startup_profile_id: string
  overall_success_score: number
  business_confidence_score: number
  overall_risk_score: number
  risk_level: string
  methodology_version: string
  scorecards: Array<{ key: string; label: string; risk_score: number; reasoning: string; positive_factors: string[]; negative_factors: string[]; suggestions: string[] }>
  recommendations: Array<{ priority: string; metric: string; recommendation: string }>
  ai_explanation?: { mode: 'ollama' | 'structured_fallback'; model?: string | null; summary?: string; strongest_evidence?: string; priority_gap?: string; next_actions?: string[]; assumptions?: string[] } | null
}
export interface FinancialPlanInput { partner_count: number; monthly_rent: number; monthly_salary_cost: number; monthly_marketing_cost: number; monthly_other_cost: number; monthly_utilities_cost: number; monthly_software_delivery_cost: number; monthly_loan_repayment: number; one_time_setup_cost: number; emergency_fund: number; expected_monthly_sales: number; average_sale_value: number; expected_monthly_revenue: number; gross_margin_percent: number }
export interface FinancialPlan { id: string; startup_profile_id: string; assumptions: Record<string, number | string>; results: Record<string, number | string | null> }
export interface AdvisorReply { response: string; mode: 'gemini' | 'structured_fallback' | 'structured'; conversation_id?: string; notice?: string | null }
export interface ProfileSuggestions { industry: string; startup_type: string; target_customers: string; description: string; next_question: string }
export interface ProfileSuggestionReply { suggestions: ProfileSuggestions; mode: 'gemini' | 'structured_fallback'; notice: string }

export const lifecycleApi = {
  listProfiles: async () => (await apiClient.get<APIResponse<StartupProfileResponse[]>>('/lifecycle-profiles')).data.data,
  createProfile: async (payload: StartupProfilePayload) => (await apiClient.post<APIResponse<StartupProfileResponse>>('/lifecycle-profiles', payload)).data.data,
  updateProfile: async (profileId: string, payload: StartupProfilePayload) => (await apiClient.patch<APIResponse<StartupProfileResponse>>(`/lifecycle-profiles/${profileId}`, payload)).data.data,
  suggestProfileFields: async (payload: { business_name: string; category: string; country?: string | null; city?: string | null }) => (await apiClient.post<APIResponse<ProfileSuggestionReply>>('/lifecycle-profiles/suggestions', payload)).data.data,
  listMilestones: async (profileId: string) => (await apiClient.get<APIResponse<LifecycleMilestoneResponse[]>>(`/lifecycle-profiles/${profileId}/milestones`)).data.data,
  updateMilestone: async (profileId: string, milestoneKey: string, completed: boolean) => (await apiClient.put<APIResponse<LifecycleMilestoneResponse>>(`/lifecycle-profiles/${profileId}/milestones/${milestoneKey}`, { completed })).data.data,
  createRiskAssessment: async (profileId: string) => (await apiClient.post<APIResponse<LifecycleRiskAssessment>>(`/lifecycle-profiles/${profileId}/risk-assessments`)).data.data,
  latestRiskAssessment: async (profileId: string) => (await apiClient.get<APIResponse<LifecycleRiskAssessment>>(`/lifecycle-profiles/${profileId}/risk-assessments/latest`)).data.data,
  createFinancialPlan: async (profileId: string, payload: FinancialPlanInput) => (await apiClient.post<APIResponse<FinancialPlan>>(`/lifecycle-profiles/${profileId}/financial-plans`, payload)).data.data,
  latestFinancialPlan: async (profileId: string) => (await apiClient.get<APIResponse<FinancialPlan>>(`/lifecycle-profiles/${profileId}/financial-plans/latest`)).data.data,
  askAdvisor: async (profileId: string, question: string, conversationId?: string) => (await apiClient.post<APIResponse<AdvisorReply>>(`/lifecycle-profiles/${profileId}/advisor`, { question, conversation_id: conversationId })).data.data,
  askAdvisorQuick: async (profileId: string, question: string) => (await apiClient.post<APIResponse<AdvisorReply>>(`/lifecycle-profiles/${profileId}/advisor/quick`, { question })).data.data,
}
