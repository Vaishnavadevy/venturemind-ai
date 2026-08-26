import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { Button } from '@/components/common/Button'
import { BrandMark } from '@/components/branding/BrandMark'
import { useAuth } from '@/features/auth/AuthContext'

const menuGroups = [
  { title: 'Research', links: [{ label: 'Startup Ideas', to: '/idea-generator' }, { label: 'Market Opportunities', to: '/tools' }, { label: 'Competitor Comparisons', to: '/research/competitor-comparisons' }, { label: 'Success & Failure Stories', to: '/stories' }] },
  { title: 'Resources', links: [{ label: 'Founder Knowledge Hub', to: '/knowledge-hub' }, { label: 'Founder Guides', to: '/learn' }, { label: 'Templates', to: '/resources/templates' }, { label: 'Startup Books', to: '/books' }, { label: 'Startup Glossary', to: '/resources/glossary' }, { label: 'Frequently asked questions', to: '/faq' }] },
  { title: 'Company', links: [{ label: 'About VentureMind', to: '/about' }, { label: 'Our Methodology', to: '/about' }, { label: 'Explainable AI', to: '/explainable-ai' }, { label: 'Contact', to: '/contact' }] },
]

export function AppNavbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [, setWorkspaceHeaderVersion] = useState(0)
  const { isAuthenticated, logout, user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const isAdmin = user?.role === 'admin'
  const isAdvisor = user?.role === 'legal_advisor' || user?.role === 'business_mentor'

  useEffect(() => {
    const refreshWorkspaceHeader = () => setWorkspaceHeaderVersion((value) => value + 1)
    window.addEventListener('venturemind-profile-saved', refreshWorkspaceHeader)
    return () => window.removeEventListener('venturemind-profile-saved', refreshWorkspaceHeader)
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const isWorkspace = isAuthenticated && location.pathname === '/workspace'
  let workspaceName = 'Current startup project'
  let workspaceSavedAt: string | null = null
  if (isWorkspace) {
    try {
      const draft = JSON.parse(localStorage.getItem('venturemind.lifecycle-profile-draft') ?? '{}') as { businessName?: string }
      workspaceName = draft.businessName?.trim() || workspaceName
      workspaceSavedAt = localStorage.getItem('venturemind.lifecycle-profile-last-saved')
    } catch { /* Keep the safe workspace-header defaults. */ }
  }

  if (isWorkspace) return <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/95"><nav className="mx-auto flex min-h-[64px] max-w-7xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-6"><Link className="flex items-center gap-2 font-bold tracking-tight" to="/dashboard"><BrandMark /><span>VentureMind <span className="text-brand-600">AI</span></span></Link><span className="hidden text-slate-300 sm:inline">/</span><Link className="text-sm font-bold text-brand-700 hover:underline" to="/dashboard">Dashboard</Link><div className="min-w-0 flex-1 border-l border-slate-200 pl-4 dark:border-slate-800"><p className="truncate text-sm font-bold">{workspaceName}</p><p className="text-xs text-emerald-700">{workspaceSavedAt ? `Saved ${new Date(workspaceSavedAt).toLocaleString()}` : 'Saving status available after your first draft'}</p></div><a className="text-sm font-semibold text-slate-600 hover:text-brand-700" href="/faq">Help</a><Button variant="ghost" onClick={() => void handleLogout()}>Sign out</Button></nav></header>

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/70 bg-white/85 backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/85">
      <nav className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link className="flex items-center gap-2 font-bold tracking-tight" to={isAdmin ? '/admin' : isAdvisor ? '/advisor-dashboard' : '/'}>
          <BrandMark />
          <span>VentureMind <span className="text-brand-600">AI</span></span>
        </Link>

        <div className="hidden items-center gap-6 lg:flex">
          {isAdmin ? <>
            <Link className="nav-link" to="/admin">Admin dashboard</Link>
            <Link className="nav-link" to="/admin/advisor-approvals">Advisor approvals</Link>
            <Link className="nav-link" to="/admin/announcements">Announcements</Link>
            <Link className="nav-link" to="/admin/users">Users</Link>
            <Link className="nav-link" to="/admin/analytics">Analytics</Link>
            <Link className="nav-link" to="/admin/feedback">Feedback</Link>
          </> : isAdvisor ? <>
            <Link className="nav-link" to="/advisor-dashboard">Advisor dashboard</Link>
            <Link className="nav-link" to="/advisor-profile">My profile</Link>
            <Link className="nav-link" to="/advisor-availability">Manage availability</Link>
          </> : isAuthenticated ? <>
            <Link className="nav-link" to="/dashboard">Dashboard</Link>
            <Link className="nav-link" to="/workspace">Startup workspace</Link>
            <Link className="nav-link" to="/registration">Registration guide</Link>
            <Link className="nav-link" to="/launch-growth">Launch &amp; growth</Link>
            <Link className="nav-link" to="/advisors">Human advisors</Link>
            <Link className="nav-link" to="/appointments">Appointments</Link>
          </> : <>
            <Link className="nav-link" to="/idea-generator">Generate Ideas</Link>
            <Link className="nav-link" to="/learn">Learn</Link>
            <Link className="nav-link" to="/tools">Free Tools</Link>
            <Link className="nav-link" to="/pricing">Pricing</Link>
            <div className="relative">
              <button className="nav-link" onClick={() => setMenuOpen((value) => !value)} aria-expanded={menuOpen}>More <span className="ml-1 text-xs">⌄</span></button>
              {menuOpen && <div className="absolute right-0 top-9 grid w-[680px] grid-cols-3 gap-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-float dark:border-slate-800 dark:bg-slate-900">
                {menuGroups.map((group) => <div key={group.title}>
                  <p className="text-xs font-bold uppercase tracking-widest text-brand-600">{group.title}</p>
                  {group.links.map((item) => <Link key={item.label} className="mt-3 block text-sm font-medium text-slate-600 hover:text-brand-600 dark:text-slate-300" to={item.to} onClick={() => setMenuOpen(false)}>{item.label}</Link>)}
                </div>)}
              </div>}
            </div>
          </>}
        </div>

        <div className="hidden items-center gap-2 sm:flex">
          {isAuthenticated ? <Button variant="ghost" onClick={() => void handleLogout()}>Sign out</Button> : <Link className="nav-link" to="/login">Log in</Link>}
          {!isAuthenticated && <Link to="/register"><Button>Start planning</Button></Link>}
        </div>

        <button className="grid h-10 w-10 place-items-center rounded-lg border border-slate-200 text-lg lg:hidden dark:border-slate-700" onClick={() => setMobileOpen((value) => !value)} aria-label="Toggle navigation">☰</button>
      </nav>

      {mobileOpen && <div className="border-t border-slate-200 bg-white px-5 py-5 dark:border-slate-800 dark:bg-slate-950 lg:hidden">
        <div className="grid gap-4 text-sm font-semibold">
          {isAdmin ? <>
            <Link to="/admin" onClick={() => setMobileOpen(false)}>Admin dashboard</Link>
            <Link to="/admin/advisor-approvals" onClick={() => setMobileOpen(false)}>Advisor approvals</Link>
            <Link to="/admin/announcements" onClick={() => setMobileOpen(false)}>Announcements</Link>
            <Link to="/admin/users" onClick={() => setMobileOpen(false)}>Users</Link>
            <Link to="/admin/analytics" onClick={() => setMobileOpen(false)}>Analytics</Link>
            <Link to="/admin/feedback" onClick={() => setMobileOpen(false)}>Feedback</Link>
          </> : isAdvisor ? <>
            <Link to="/advisor-dashboard" onClick={() => setMobileOpen(false)}>Advisor dashboard</Link>
            <Link to="/advisor-profile" onClick={() => setMobileOpen(false)}>My profile</Link>
            <Link to="/advisor-availability" onClick={() => setMobileOpen(false)}>Manage availability</Link>
          </> : isAuthenticated ? <>
            <Link to="/dashboard" onClick={() => setMobileOpen(false)}>Dashboard</Link>
            <Link to="/workspace" onClick={() => setMobileOpen(false)}>Startup workspace</Link>
            <Link to="/registration" onClick={() => setMobileOpen(false)}>Registration guide</Link>
            <Link to="/launch-growth" onClick={() => setMobileOpen(false)}>Launch &amp; growth</Link>
            <Link to="/advisors" onClick={() => setMobileOpen(false)}>Human advisors</Link>
            <Link to="/appointments" onClick={() => setMobileOpen(false)}>Appointments</Link>
          </> : <>
            <Link to="/idea-generator" onClick={() => setMobileOpen(false)}>Generate Ideas</Link>
            <Link to="/learn" onClick={() => setMobileOpen(false)}>Learn</Link>
            <Link to="/tools" onClick={() => setMobileOpen(false)}>Free Tools</Link>
            <Link to="/pricing" onClick={() => setMobileOpen(false)}>Pricing</Link>
            <Link className="rounded-lg bg-brand-600 px-4 py-3 text-center text-white" to="/register" onClick={() => setMobileOpen(false)}>Start planning</Link>
          </>}
        </div>
      </div>}
    </header>
  )
}
