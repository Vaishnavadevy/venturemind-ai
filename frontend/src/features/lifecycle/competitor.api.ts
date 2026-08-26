import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'

export interface CompetitorSearchPayload {
  business_category: string
  industry: string | null
  city: string | null
  district: string | null
  country: string
  max_results: number
}

export interface CompetitorPlace {
  place_id: string
  name: string
  address: string | null
  primary_type: string | null
  rating: number | null
  user_rating_count: number | null
  price_level: string | null
  website_url: string | null
  maps_url: string | null
}

export interface CompetitorSearchResult {
  provider_configured: boolean
  query: string
  maps_search_url: string
  competitors: CompetitorPlace[]
  notice: string | null
}

export const competitorApi = {
  search: async (payload: CompetitorSearchPayload) => (await apiClient.post<APIResponse<CompetitorSearchResult>>('/competitors/search', payload)).data.data,
}
