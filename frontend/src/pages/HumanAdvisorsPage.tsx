import { useEffect, useMemo, useState } from 'react'
import type { AxiosError } from 'axios'
import { Navigate } from 'react-router-dom'
import { apiClient } from '@/api/client'
import { Button } from '@/components/common/Button'
import { LoadingState } from '@/components/common/LoadingState'
import { useAuth } from '@/features/auth/AuthContext'
import type { APIResponse } from '@/types/api'

type Slot = { id: string; starts_at: string; ends_at: string; consultation_type: 'online' | 'in_person' }
type Service = { name: string; fee_lkr: number; description?: string }
type Advisor = { id: string; full_name: string; role: string; specialisation: string; verification_status: string; bio?: string | null; languages: string[]; consultation_fee?: number | null; office_address?: string | null; service_fees?: Service[] }

function defaultServicesFor(advisor: Advisor): Service[] {
  const legalAdvisor = advisor.role.toLowerCase().includes('legal')
  return legalAdvisor
    ? [
        { name: 'General consultation', fee_lkr: 3000 },
        { name: 'Business registration and name reservation', fee_lkr: 5000 },
        { name: 'TIN and tax registration guidance', fee_lkr: 4000 },
        { name: 'Licence and compliance review', fee_lkr: 6500 },
      ]
    : [
        { name: 'General business consultation', fee_lkr: 3000 },
        { name: 'Startup planning session', fee_lkr: 4500 },
        { name: 'Marketing and growth planning', fee_lkr: 5000 },
        { name: 'Financial plan review', fee_lkr: 6000 },
      ]
}

export function HumanAdvisorsPage() {
  const { user } = useAuth(); const [advisors, setAdvisors] = useState<Advisor[]>([]); const [selected, setSelected] = useState<Advisor | null>(null); const [slots, setSlots] = useState<Slot[]>([]); const [loading, setLoading] = useState(true); const [submitting, setSubmitting] = useState(false); const [topic, setTopic] = useState(''); const [message, setMessage] = useState(''); const [consultationType, setConsultationType] = useState<'online' | 'in_person'>('online'); const [slotId, setSlotId] = useState(''); const [serviceName, setServiceName] = useState(''); const [notice, setNotice] = useState('')
  const services = useMemo<Service[]>(() => {
    if (!selected) return []
    const configured = selected.service_fees?.filter((item) => item.name && item.fee_lkr >= 0) ?? []
    const fallback = defaultServicesFor(selected)
    const merged = [...configured, ...fallback.filter((fallbackItem) => !configured.some((item) => item.name === fallbackItem.name))]
    return merged.length ? merged : fallback
  }, [selected]); const chosen = services.find((item) => item.name === serviceName) ?? services[0]
  const matchingSlots = slots.filter((slot) => slot.consultation_type === consultationType)
  useEffect(() => { apiClient.get<APIResponse<Advisor[]>>('/human-advisors').then(({ data }) => setAdvisors(data.data)).catch(() => setNotice('Advisor profiles could not be loaded. Confirm that the backend and latest database migration are running.')).finally(() => setLoading(false)) }, [])
  useEffect(() => { if (!selected) return; setServiceName(selected.service_fees?.[0]?.name ?? defaultServicesFor(selected)[0].name); apiClient.get<APIResponse<Slot[]>>(`/human-advisors/${selected.id}/available-slots`).then(({ data }) => setSlots(data.data)).catch(() => setSlots([])) }, [selected])
  const submit = async () => {
    if (!selected) return
    setSubmitting(true)
    setNotice('')
    try {
      const { data } = await apiClient.post<APIResponse<{ id: string }>>('/human-advisors/booking-requests', { advisor_id: selected.id, consultation_type: consultationType, topic, message, availability_slot_id: slotId || null, service_name: chosen?.name })
      try {
        await apiClient.post(`/human-advisors/booking-requests/${data.data.id}/payment`)
        setNotice(`Your ${chosen?.name ?? 'consultation'} request was sent. LKR ${chosen?.fee_lkr.toLocaleString() ?? '0'} was recorded as a demonstration payment; no money was charged.`)
      } catch {
        setNotice('Your booking was sent successfully, but the demonstration payment record could not be created. The booking remains visible to the advisor.')
      }
      setSelected(null); setTopic(''); setMessage(''); setSlotId('')
    } catch (caughtError) {
      const error = caughtError as AxiosError<{ detail?: string; message?: string }>
      const detail = error.response?.data?.detail ?? error.response?.data?.message
      if (!error.response) setNotice('The booking API could not be reached. Confirm the FastAPI backend is running on port 8000.')
      else if (error.response.status >= 500) setNotice('The booking service database is not ready. Apply the backend migrations, restart FastAPI, then submit again.')
      else setNotice(detail ?? 'The booking request could not be sent. Check the required fields and try again.')
    } finally { setSubmitting(false) }
  }
  if (user?.role === 'legal_advisor' || user?.role === 'business_mentor') return <Navigate replace to="/advisor-dashboard" />
  if (loading) return <LoadingState label="Loading approved advisors..." />
  return <div className="mx-auto max-w-6xl space-y-6">
    <header><p className="page-eyebrow">Approved advisor directory</p><h1 className="page-title">Book a Business Mentor or Legal Advisor</h1><p className="mt-2 max-w-3xl text-slate-600">Choose a verified advisor, service, fee, and an advisor-published appointment time. Payment is demonstration tracking only until a real gateway is configured.</p></header>
    {notice && <p className="rounded-xl bg-brand-50 p-4 text-sm text-brand-800">{notice}</p>}
    <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{advisors.map((advisor) => <article key={advisor.id} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card"><span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700">{advisor.role}</span><h2 className="mt-4 text-xl font-bold">{advisor.full_name}</h2><p className="mt-2 text-sm leading-6 text-slate-600">{advisor.bio || advisor.specialisation}</p><p className="mt-3 text-sm font-semibold">{advisor.specialisation}</p>{advisor.languages.length > 0 && <p className="mt-2 text-xs text-slate-500">Languages: {advisor.languages.join(', ')}</p>}{advisor.office_address && <p className="mt-2 text-xs text-slate-500">Office: {advisor.office_address}</p>}<p className="mt-4 text-sm font-bold text-brand-700">From LKR {(advisor.service_fees?.[0]?.fee_lkr ?? advisor.consultation_fee ?? 3000).toLocaleString()}</p><p className="mt-2 text-xs font-semibold text-emerald-700">{advisor.verification_status}</p><Button className="mt-5 w-full" onClick={() => { setSelected(advisor); setNotice('') }}>Book appointment</Button></article>)}</div>
    {!advisors.length && <section className="rounded-2xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-500">No approved advisors are available yet.</section>}
    {selected && <section className="rounded-2xl border border-brand-200 bg-white p-6 shadow-card"><h2 className="text-xl font-bold">Book with {selected.full_name}</h2><p className="mt-1 text-sm text-slate-500">Choose the service and a real published date/time before confirming.</p><div className="mt-4 grid gap-4 sm:grid-cols-2"><label className="text-sm font-semibold">Service<select value={serviceName} onChange={(event) => setServiceName(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal">{services.map((item) => <option key={item.name} value={item.name}>{item.name} — LKR {item.fee_lkr.toLocaleString()}</option>)}</select></label><div className="rounded-lg bg-brand-50 p-3 text-sm"><strong>Demonstration fee</strong><p className="mt-1 text-xl font-extrabold text-brand-800">LKR {chosen?.fee_lkr.toLocaleString()}</p><p className="mt-1 text-xs text-brand-700">No money is charged in this project.</p></div><label className="text-sm font-semibold">Consultation type<select value={consultationType} onChange={(event) => { setConsultationType(event.target.value as 'online' | 'in_person'); setSlotId('') }} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal"><option value="online">Online consultation</option><option value="in_person">In-person consultation</option></select></label><label className="text-sm font-semibold">Available appointment slot<select value={slotId} onChange={(event) => setSlotId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal"><option value="" disabled>Select an available date and time</option>{matchingSlots.map((slot) => <option key={slot.id} value={slot.id}>{new Date(slot.starts_at).toLocaleString()} – {new Date(slot.ends_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</option>)}</select>{matchingSlots.length === 0 && <p className="mt-2 text-xs leading-5 text-amber-700">No {consultationType === 'online' ? 'online' : 'in-person'} slots are published. The advisor must add availability first.</p>}</label><label className="text-sm font-semibold sm:col-span-2">Topic<input value={topic} onChange={(event) => setTopic(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal" placeholder="Example: Business registration" /></label></div><label className="mt-4 block text-sm font-semibold">Message<textarea value={message} onChange={(event) => setMessage(event.target.value)} rows={4} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal" placeholder="Briefly describe the help you need..." /></label><div className="mt-5 flex gap-3"><Button disabled={submitting || !slotId || topic.trim().length < 3 || message.trim().length < 10} onClick={() => void submit()}>{submitting ? 'Saving booking…' : 'Confirm booking and record payment'}</Button><Button variant="secondary" onClick={() => setSelected(null)}>Cancel</Button></div></section>}
  </div>
}
