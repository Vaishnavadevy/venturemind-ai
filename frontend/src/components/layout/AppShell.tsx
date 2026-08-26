import { Outlet } from 'react-router-dom'
import { AppFooter } from './AppFooter'
import { AppNavbar } from '@/components/navigation/AppNavbar'
import { GlobalPageNavigation } from '@/components/common/GlobalPageNavigation'
import { FounderAdvisorChatWidget } from '@/components/chat/FounderAdvisorChatWidget'

export function AppShell() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_8%_0%,_rgba(221,214,254,0.72),_transparent_31rem),radial-gradient(circle_at_92%_22%,_rgba(186,230,253,0.42),_transparent_28rem),linear-gradient(180deg,_#f8fafc_0%,_#f5f3ff_48%,_#f8fafc_100%)] dark:bg-[radial-gradient(circle_at_10%_0%,_rgba(76,29,149,0.35),_transparent_28rem),linear-gradient(180deg,_#020617,_#0f172a)]">
      <AppNavbar />
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:py-12"><Outlet /></main>
      <AppFooter />
      <GlobalPageNavigation />
      <FounderAdvisorChatWidget />
    </div>
  )
}
