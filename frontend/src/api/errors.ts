import { isAxiosError } from 'axios'
import type { APIError } from '@/types/api'

export function apiErrorDetails(error: unknown): APIError['error'] | null {
  if (!isAxiosError<APIError>(error)) return null
  return error.response?.data?.error ?? null
}

export function apiErrorMessage(error: unknown, fallback: string): string {
  return apiErrorDetails(error)?.message ?? fallback
}
