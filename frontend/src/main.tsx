import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from '@/App'
import { ThemeProvider } from '@/context/ThemeContext'
import { AuthProvider } from '@/features/auth/AuthContext'
import { AppErrorBoundary } from '@/components/common/AppErrorBoundary'
import '@/index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <AppErrorBoundary><AuthProvider><App /></AuthProvider></AppErrorBoundary>
    </ThemeProvider>
  </StrictMode>,
)
