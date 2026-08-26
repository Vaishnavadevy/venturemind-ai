import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'

export type DevelopmentStage = 'idea' | 'research' | 'mvp' | 'prototype' | 'testing' | 'launched' | 'growth'

export interface StartupSubmission {
  startup_name: string
  industry: string
  country: string
  target_audience: string
  problem_statement: string
  proposed_solution: string
  business_model: string
  revenue_model: string
  development_stage: DevelopmentStage
  budget_amount: number | null
  budget_currency: string | null
  competitors: string[]
  additional_notes: string | null
}

export interface ProjectSummary {
  id: string
  name: string
  industry: string
  development_stage: DevelopmentStage
  status: string
  latest_evaluation_id: string | null
  latest_score: number | null
}

export const projectApi = {
  create: (payload: StartupSubmission) => apiClient.post<APIResponse<{ project: { id: string }; startup_idea: { id: string }; evaluation_id: string }>>('/projects', payload),
  get: async (projectId: string) => (await apiClient.get<APIResponse<ProjectSummary>>(`/projects/${projectId}`)).data.data,
  archive: (projectId: string) => apiClient.patch<APIResponse<ProjectSummary>>(`/projects/${projectId}`, { status: 'archived' }),
}
