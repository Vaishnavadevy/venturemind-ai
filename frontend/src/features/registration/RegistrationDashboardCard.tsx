import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { apiClient } from '@/api/client'
import { Button } from '@/components/common/Button'
import type { APIResponse } from '@/types/api'

type Journey = { mode: 'guide' | 'demo'; proposed_company_name: string | null; progress_percentage: number; items: Array<{ status: string }> }

/** Compact founder-dashboard entry point; the detailed workflow remains on /registration. */
export function RegistrationDashboardCard() {
  const [journey, setJourney] = useState<Journey | null>(null)
  const [loading, setLoading] = useState(true)
  const [available, setAvailable] = useState(true)
  const [starting, setStarting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    apiClient.get<APIResponse<Journey>>('/business-registration/current')
      .then(({ data }) => setJourney(data.data))
      .catch(() => { setJourney(null); setAvailable(false) })
      .finally(() => setLoading(false))
  }, [])

  const start = async () => {
    setStarting(true)
    try {
      await apiClient.post('/business-registration/start', { mode: 'guide' })
      navigate('/registration')
    } finally { setStarting(false) }
  }

  const completed = journey?.items.filter((item) => item.status === 'completed' || item.status === 'approved').length ?? 0
  return <section className="rounded-3xl border border-cyan-100 bg-gradient-to-br from-cyan-50 via-white to-violet-50 p-5 shadow-[0_16px_45px_-30px_rgba(15,23,42,0.42)]">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm font-bold uppercase tracking-wider text-violet-700">Legal setup</p><h2 className="mt-1 text-xl font-bold text-slate-950">Business registration journey</h2></div><span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-600 shadow-sm">Educational guidance</span></div>
    {loading ? <div className="mt-4 h-16 animate-pulse rounded-2xl bg-slate-100" /> : journey ? <><p className="mt-3 text-sm leading-6 text-slate-600">{journey.proposed_company_name || 'Your startup'} · {journey.mode === 'demo' ? 'Demo registration workflow' : 'Official-resource preparation guide'}</p><div className="mt-4 flex items-center gap-3"><strong className="text-2xl text-slate-950">{journey.progress_percentage}%</strong><div className="flex-1"><div className="h-2 overflow-hidden rounded-full bg-slate-200"><div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-600" style={{ width: `${journey.progress_percentage}%` }} /></div><p className="mt-1 text-xs text-slate-500">{completed} of {journey.items.length} registration steps completed</p></div></div><Button className="mt-4" onClick={() => navigate('/registration')}>Continue registration guide</Button></> : available ? <><p className="mt-3 text-sm leading-6 text-slate-600">After completing your startup profile and planning steps, prepare your company-registration journey using official resources. VentureMind does not submit a real registration application.</p><Button className="mt-4" disabled={starting} onClick={() => void start()}>{starting ? 'Starting…' : 'Start Registration Guide'}</Button></> : <p className="mt-3 rounded-xl bg-amber-50 p-3 text-sm leading-6 text-amber-900">The registration tracker is temporarily unavailable while its database setup is completed. Your dashboard and core planning tools remain available.</p>}
  </section>
}
