import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'
import { environment } from '@/config/environment'

export function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  return isAuthenticated || environment.demoMode ? <Outlet /> : <Navigate replace to="/login" state={{ from: location }} />
}
