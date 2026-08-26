import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'
import type { AuthUser, TokenPair } from './auth.types'

export const authApi = {
  register: (payload: { full_name: string; email: string; password: string }) =>
    apiClient.post<APIResponse<AuthUser>>('/auth/register', payload),
  login: (payload: { email: string; password: string }) =>
    apiClient.post<APIResponse<TokenPair>>('/auth/login', payload),
  refresh: (refresh_token: string) => apiClient.post<APIResponse<TokenPair>>('/auth/refresh', { refresh_token }),
  logout: (refresh_token: string) => apiClient.post<APIResponse<null>>('/auth/logout', { refresh_token }),
  getCurrentUser: () => apiClient.get<APIResponse<AuthUser>>('/auth/me'),
  verifyEmail: (token: string) => apiClient.post<APIResponse<null>>('/auth/verify-email', { token }),
  forgotPassword: (email: string) => apiClient.post<APIResponse<null>>('/auth/forgot-password', { email }),
  resetPassword: (token: string, newPassword: string) => apiClient.post<APIResponse<null>>('/auth/reset-password', { token, new_password: newPassword }),
}
