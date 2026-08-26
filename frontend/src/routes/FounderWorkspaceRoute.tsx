import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'

/** Keeps founder-only creation screens out of administrator and advisor workflows. */
export function FounderWorkspaceRoute() {
  const { user } = useAuth()
  if (user?.role === 'admin') return <Navigate replace to="/admin" />
  if (user?.role === 'legal_advisor' || user?.role === 'business_mentor') return <Navigate replace to="/advisor-dashboard" />
  return <Outlet />
}
