import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { environment } from '@/config/environment'

const accessKey = 'venturemind.access-token'
const refreshKey = 'venturemind.refresh-token'
const userKey = 'venturemind.user'

type RetriableRequest = InternalAxiosRequestConfig & { _venturemindRetried?: boolean }
let refreshInFlight: Promise<string> | null = null

function clearExpiredSession() {
  localStorage.removeItem(accessKey)
  localStorage.removeItem(refreshKey)
  localStorage.removeItem(userKey)
}

export const apiClient = axios.create({
  baseURL: environment.apiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(accessKey)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const request = error.config as RetriableRequest | undefined
    const isAuthenticationRequest = request?.url?.includes('/auth/')
    if (error.response?.status !== 401 || !request || request._venturemindRetried || isAuthenticationRequest || environment.demoMode) {
      return Promise.reject(error)
    }

    const refreshToken = localStorage.getItem(refreshKey)
    if (!refreshToken) {
      clearExpiredSession()
      window.location.assign('/login')
      return Promise.reject(error)
    }

    request._venturemindRetried = true
    try {
      refreshInFlight ??= apiClient.post('/auth/refresh', { refresh_token: refreshToken }).then((response) => {
        const tokens = response.data.data as { access_token: string; refresh_token: string; user: unknown }
        localStorage.setItem(accessKey, tokens.access_token)
        localStorage.setItem(refreshKey, tokens.refresh_token)
        localStorage.setItem(userKey, JSON.stringify(tokens.user))
        return tokens.access_token
      }).finally(() => { refreshInFlight = null })
      const accessToken = await refreshInFlight
      request.headers.Authorization = `Bearer ${accessToken}`
      return apiClient(request)
    } catch (refreshError) {
      clearExpiredSession()
      window.location.assign('/login')
      return Promise.reject(refreshError)
    }
  },
)
