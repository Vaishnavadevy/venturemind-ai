import { useEffect, useState } from 'react'
import type { AxiosError } from 'axios'

import { apiClient } from '@/api/client'
import { Button } from '@/components/common/Button'
import { LoadingState } from '@/components/common/LoadingState'
import { lifecycleApi, type StartupProfileResponse } from '@/features/lifecycle/lifecycle.api'
import type { APIResponse } from '@/types/api'

type Status = 'not_started' | 'in_progress' | 'completed' | 'waiting_for_review' | 'approved' | 'requires_action'
type Item = { id: string; item_key: string; step_number: number; title: string; description: string; category: string; official_url: string | null; status: Status; completed_at: string | null }
type Resource = { title: string; description: string; url: string; category: string; official: boolean }
type Journey = { id: string; mode: 'guide' | 'demo'; company_type: string | null; proposed_company_name: string | null; overall_status: string; is_demo: boolean; progress_percentage: number; items: Item[]; resources: Resource[] }

const statusLabels: Record<Status, string> = { not_started: 'Not started', in_progress: 'In progress', completed: 'Completed', waiting_for_review: 'Waiting for review', approved: 'Approved', requires_action: 'Requires action' }
const statusClasses: Record<Status, string> = { not_started: 'bg-slate-100 text-slate-700', in_progress: 'bg-sky-100 text-sky-800', completed: 'bg-emerald-100 text-emerald-800', waiting_for_review: 'bg-amber-100 text-amber-800', approved: 'bg-emerald-100 text-emerald-800', requires_action: 'bg-rose-100 text-rose-800' }

export function BusinessRegistrationPage() {
  const [journey, setJourney] = useState<Journey | null>(null)
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState('')
  const [companyType, setCompanyType] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [savedProfiles, setSavedProfiles] = useState<StartupProfileResponse[]>([])

  const load = async () => {
    try {
      const [journeyResult, profiles] = await Promise.all([
        apiClient.get<APIResponse<Journey>>('/business-registration/current'),
        lifecycleApi.listProfiles(),
      ])
      setJourney(journeyResult.data.data)
      setCompanyType(journeyResult.data.data.company_type ?? '')
      setCompanyName(journeyResult.data.data.proposed_company_name ?? '')
      setSavedProfiles(profiles)
    } catch {
      setJourney(null)
      try { setSavedProfiles(await lifecycleApi.listProfiles()) } catch { /* The page renders a clear signed-in error below. */ }
    } finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [])
  const start = async (mode: 'guide' | 'demo') => {
    if (!savedProfiles.length) {
      setNotice('Create and save a startup profile first. The guide will then attach its checklist to that business.')
      return
    }
    try {
      const { data } = await apiClient.post<APIResponse<Journey>>('/business-registration/start', { mode })
      setJourney(data.data)
      setCompanyType(data.data.company_type ?? '')
      setCompanyName(data.data.proposed_company_name ?? '')
      setNotice(mode === 'demo' ? 'Demo registration started. No information will be sent to a government authority.' : 'Registration guide started. Progress is saved to your account.')
    } catch (caughtError) {
      const error = caughtError as AxiosError<{ detail?: string }>
      if (error.response?.status === 401) setNotice('Your session has expired. Please sign in again, then reopen the guide.')
      else if (error.response?.status && error.response.status >= 500) setNotice('The registration guide database is not ready yet. Run the latest backend migration, restart the API, and try again.')
      else setNotice(error.response?.data?.detail ?? 'The registration guide could not be started. Please try again.')
    }
  }
  const saveDetails = async () => { if (!journey) return; try { const { data } = await apiClient.patch<APIResponse<Journey>>('/business-registration/current', { company_type: companyType, proposed_company_name: companyName }); setJourney(data.data); setNotice('Registration preparation details saved.') } catch { setNotice('Registration details could not be saved.') } }
  const changeStatus = async (item: Item, status: Status) => { try { const { data } = await apiClient.patch<APIResponse<Journey>>(`/business-registration/items/${item.id}`, { status }); setJourney(data.data); setNotice(`${item.title} updated.`) } catch { setNotice('Checklist status could not be saved.') } }

  if (loading) return <LoadingState label="Loading business registration guide…" />
  if (!journey) return <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6"><section className="rounded-[2rem] bg-slate-950 p-8 text-white shadow-2xl"><p className="text-sm font-bold uppercase tracking-[0.18em] text-violet-300">Business registration guidance</p><h1 className="mt-3 text-3xl font-bold">Prepare your registration journey with confidence.</h1><p className="mt-4 max-w-3xl leading-7 text-slate-300">VentureMind provides educational guidance and workflow support. It does not perform legal company registration, submit applications, confirm fees, or connect to government systems. Always verify current requirements with the official authority or a qualified advisor.</p>{savedProfiles.length > 0 && <p className="mt-5 rounded-xl bg-emerald-400/15 p-3 text-sm text-emerald-100">Ready to start for: <strong>{savedProfiles[0].business_name}</strong></p>}<div className="mt-7 flex flex-wrap gap-3"><Button onClick={() => void start('guide')}>Start Registration Guide</Button><Button variant="secondary" onClick={() => void start('demo')}>Try Demo Registration</Button><a className="rounded-xl border border-white/30 px-4 py-2.5 text-sm font-bold hover:bg-white/10" href="https://eroc.drc.gov.lk" target="_blank" rel="noreferrer">Official Registration Portal ↗</a></div>{notice && <p className="mt-5 rounded-xl bg-white/10 p-3 text-sm">{notice}</p>}</section></main>

  return <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6"><section className="rounded-[2rem] bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 p-7 text-white shadow-2xl"><div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-start"><div><p className="text-sm font-bold uppercase tracking-[0.18em] text-violet-300">Sri Lanka business registration guide</p><h1 className="mt-2 text-3xl font-bold">Your company registration journey</h1><p className="mt-3 max-w-3xl leading-7 text-slate-300">Educational guidance only. VentureMind does not legally register your company or submit information to any government service.</p></div><span className={`w-fit rounded-full px-3 py-1 text-xs font-bold ${journey.is_demo ? 'bg-amber-300 text-amber-950' : 'bg-cyan-100 text-cyan-950'}`}>{journey.is_demo ? 'DEMO MODE' : 'GUIDANCE MODE'}</span></div><div className="mt-6 flex flex-wrap items-center gap-4"><strong className="text-3xl">{journey.progress_percentage}%</strong><span className="text-sm text-slate-300">Registration preparation progress</span><div className="min-w-48 flex-1"><div className="h-2 overflow-hidden rounded-full bg-white/15"><div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-400" style={{ width: `${journey.progress_percentage}%` }} /></div></div></div></section>

    {notice && <p className="rounded-2xl border border-violet-200 bg-violet-50 p-4 text-sm font-medium text-violet-900">{notice}</p>}

    <section className="grid gap-5 lg:grid-cols-[1fr_1.4fr]"><article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"><p className="text-sm font-bold uppercase tracking-wider text-violet-700">Registration preparation</p><h2 className="mt-1 text-xl font-bold">Company details</h2><label className="mt-4 block text-sm font-bold">Company type<select className="mt-2 w-full rounded-xl border border-slate-300 bg-white p-3" value={companyType} onChange={(event) => setCompanyType(event.target.value)}><option value="">Select for planning</option><option>Private Limited Company</option><option>Public Limited Company</option><option>Sole Proprietorship</option><option>Partnership</option></select></label><label className="mt-4 block text-sm font-bold">Proposed company name<input className="mt-2 w-full rounded-xl border border-slate-300 p-3" value={companyName} onChange={(event) => setCompanyName(event.target.value)} placeholder="Example: NovaTech Solutions (Pvt) Ltd" /></label><Button className="mt-4" onClick={() => void saveDetails()}>Save preparation details</Button><p className="mt-4 text-xs leading-5 text-slate-500">A saved name is only a planning entry. Use official name search before assuming it is available.</p></article>
      <article className="rounded-3xl border border-amber-200 bg-amber-50 p-5"><p className="text-sm font-bold uppercase tracking-wider text-amber-800">Important disclaimer</p><h2 className="mt-1 text-xl font-bold text-slate-950">Government registration remains external</h2><p className="mt-3 text-sm leading-6 text-slate-700">Requirements, fees, procedures, and beneficial-ownership obligations can change. Update your progress manually after using official channels. Do not upload sensitive documents to this guide unless an authorised advisor securely requests them through the Advisor module.</p><div className="mt-4 flex flex-wrap gap-3"><a className="text-sm font-bold text-violet-700 hover:underline" href="https://eroc.drc.gov.lk" target="_blank" rel="noreferrer">Open official eROC portal ↗</a><a className="text-sm font-bold text-violet-700 hover:underline" href="https://drc.gov.lk/en/" target="_blank" rel="noreferrer">Registrar of Companies ↗</a></div></article></section>

    <section><p className="page-eyebrow">Guided checklist</p><h2 className="page-title">Ten steps to prepare and track</h2><div className="mt-4 grid gap-4 lg:grid-cols-2">{journey.items.map((item) => <article key={item.id} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex flex-wrap items-start justify-between gap-3"><div className="flex gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-violet-100 text-sm font-extrabold text-violet-800">{item.step_number}</span><div><p className="text-xs font-bold uppercase tracking-wider text-slate-500">{item.category}</p><h3 className="font-bold text-slate-950">{item.title}</h3></div></div><span className={`rounded-full px-2.5 py-1 text-xs font-bold ${statusClasses[item.status]}`}>{statusLabels[item.status]}</span></div><p className="mt-3 text-sm leading-6 text-slate-600">{item.description}</p><div className="mt-4 flex flex-wrap items-center gap-3">{item.official_url && <a className="text-sm font-bold text-violet-700 hover:underline" href={item.official_url} target="_blank" rel="noreferrer">Official reference ↗</a>}<select aria-label={`${item.title} status`} className="rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm" value={item.status} onChange={(event) => void changeStatus(item, event.target.value as Status)}>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div></article>)}</div></section>

    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"><p className="text-sm font-bold uppercase tracking-wider text-violet-700">Official resources</p><h2 className="mt-1 text-xl font-bold">Use verified external sources</h2><div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">{journey.resources.map((resource) => <a key={resource.title} href={resource.url} target="_blank" rel="noreferrer" className="rounded-2xl border border-slate-200 p-4 transition hover:border-violet-300 hover:bg-violet-50"><p className="text-xs font-bold uppercase tracking-wider text-slate-500">{resource.category} · Official</p><h3 className="mt-2 font-bold text-slate-950">{resource.title}</h3><p className="mt-2 text-sm leading-5 text-slate-600">{resource.description}</p><p className="mt-3 text-sm font-bold text-violet-700">Open resource ↗</p></a>)}</div></section>
  </main>
}
