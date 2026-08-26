import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { authApi } from './auth.api'
import type { AuthUser, TokenPair } from './auth.types'
import { environment } from '@/config/environment'

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<AuthUser>
  logout: () => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)
const accessKey = 'venturemind.access-token'
const refreshKey = 'venturemind.refresh-token'
const userKey = 'venturemind.user'
const demoUser: AuthUser = { id: 'demo-user', email: 'demo@venturemind.local', full_name: 'Demo Founder', role: 'user', is_email_verified: true, created_at: new Date(0).toISOString() }

function persistSession(tokens: TokenPair) {
  localStorage.setItem(accessKey, tokens.access_token)
  localStorage.setItem(refreshKey, tokens.refresh_token)
  localStorage.setItem(userKey, JSON.stringify(tokens.user))
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const serialized = localStorage.getItem(userKey)
    if (!serialized || (!environment.demoMode && !localStorage.getItem(accessKey))) return null
    try { return JSON.parse(serialized) as AuthUser } catch { return null }
  })

  const login = useCallback(async (email: string, password: string) => {
    if (environment.demoMode) { setUser(demoUser); return demoUser }
    const { data } = await authApi.login({ email, password })
    persistSession(data.data)
    setUser(data.data.user)
    return data.data.user
  }, [])

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    if (environment.demoMode) { setUser({ ...demoUser, full_name: fullName, email }); return }
    await authApi.register({ full_name: fullName, email, password })
  }, [])

  const logout = useCallback(async () => {
    if (environment.demoMode) {
      setUser(null)
      return
    }
    const refreshToken = localStorage.getItem(refreshKey)
    try { if (refreshToken) await authApi.logout(refreshToken) } finally {
      localStorage.removeItem(accessKey); localStorage.removeItem(refreshKey); localStorage.removeItem(userKey); setUser(null)
    }
  }, [])

  const value = useMemo(() => ({ user, isAuthenticated: Boolean(user && (environment.demoMode || localStorage.getItem(accessKey))), login, logout, register }), [user, login, logout, register])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider.')
  return context
}
