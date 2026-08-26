import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { apiClient } from '@/api/client'
import { Button } from '@/components/common/Button'
import type { APIResponse } from '@/types/api'

type Recommendation = {
  id: string | null
  key: string
  title: string
  reason: string
  priority: 'High' | 'Medium' | 'Low'
  related_module: string
  action_label: string
  action_path: string
  status: 'open' | 'completed'
  completed_at: string | null
}

type Snapshot = {
  startup_profile_id: string | null
  generated_from: string[]
  recommendations: Recommendation[]
}

const priorityClass: Record<Recommendation['priority'], string> = {
  High: 'bg-rose-100 text-rose-800',
  Medium: 'bg-amber-100 text-amber-800',
  Low: 'bg-emerald-100 text-emerald-800',
}

/** A standalone dashboard feature; it does not alter lifecycle completion or source records. */
export function SmartRecommendationsPanel() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState<string | null>(null)

  const load = async () => {
    try {
      setError('')
      const response = await apiClient.get<APIResponse<Snapshot>>('/recommendations/current')
      setSnapshot(response.data.data)
    } catch {
      setError('Recommendations are not ready yet. Complete your profile and risk analysis first, then refresh this panel.')
    }
  }

  useEffect(() => { void load() }, [])

  const mark = async (recommendation: Recommendation, completed: boolean) => {
    setBusy(recommendation.key)
    try {
      const response = await apiClient.patch<APIResponse<Recommendation>>(`/recommendations/${recommendation.key}`, { completed })
      setSnapshot((current) => current ? {
        ...current,
        recommendations: current.recommendations.map((item) => item.key === recommendation.key ? response.data.data : item),
      } : current)
    } catch {
      setError('This recommendation status could not be saved.')
    } finally {
      setBusy(null)
    }
  }

  return <section className="rounded-3xl border border-cyan-100 bg-gradient-to-br from-white via-cyan-50/70 to-violet-50/70 p-5 shadow-[0_16px_45px_-30px_rgba(15,23,42,0.42)]">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <p className="text-sm font-bold uppercase tracking-wider text-violet-700">Smart recommendations</p>
        <h2 className="mt-1 text-xl font-bold text-slate-950">Your highest-value next actions</h2>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">Generated only from your saved VentureMind profile, risk, finance, requirements, employee, and task records.</p>
      </div>
      <button className="text-sm font-bold text-violet-700 hover:underline" onClick={() => void load()}>Refresh</button>
    </div>
    {error && <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900"><strong>Recommendations will appear here.</strong><p className="mt-1">{error}</p><Link className="mt-2 inline-block font-bold text-violet-700 hover:underline" to="/workspace#risk-analysis">Open risk analysis →</Link></div>}
    {!snapshot && !error ? <div className="mt-4 h-32 animate-pulse rounded-2xl bg-slate-100" /> : snapshot?.recommendations.length === 0 ? <div className="mt-4 rounded-2xl bg-white/80 p-5 text-sm leading-6 text-slate-600">Save a startup profile to receive evidence-based recommendations. Recommendations will appear only when VentureMind finds a relevant saved-data gap.</div> : snapshot ? <div className="mt-4 grid gap-3 lg:grid-cols-2 xl:grid-cols-3">{snapshot.recommendations.map((recommendation, index) => <article key={recommendation.key} className={`rounded-2xl border p-4 ${recommendation.status === 'completed' ? 'border-emerald-200 bg-emerald-50/70' : 'border-white bg-white/90'}`}>
      <div className="flex items-center justify-between gap-2"><span className="grid h-7 w-7 place-items-center rounded-full bg-slate-100 text-xs font-extrabold text-slate-700">{recommendation.status === 'completed' ? '✓' : index + 1}</span><span className={`rounded-full px-2.5 py-1 text-xs font-bold ${recommendation.status === 'completed' ? 'bg-emerald-100 text-emerald-800' : priorityClass[recommendation.priority]}`}>{recommendation.status === 'completed' ? 'Marked complete' : `${recommendation.priority} priority`}</span></div>
      <h3 className="mt-3 font-bold text-slate-950">{recommendation.title}</h3>
      <p className="mt-2 min-h-12 text-sm leading-5 text-slate-600">{recommendation.reason}</p>
      <p className="mt-3 text-xs font-bold uppercase tracking-wide text-slate-500">{recommendation.related_module}</p>
      <div className="mt-4 flex flex-wrap gap-2"><Link to={recommendation.action_path}><Button className="text-sm">{recommendation.action_label}</Button></Link><Button variant="secondary" className="text-sm" disabled={busy === recommendation.key} onClick={() => void mark(recommendation, recommendation.status !== 'completed')}>{busy === recommendation.key ? 'Saving…' : recommendation.status === 'completed' ? 'Undo' : 'Mark complete'}</Button></div>
    </article>)}</div> : null}
  </section>
}
