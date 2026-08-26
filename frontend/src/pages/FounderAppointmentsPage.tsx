import { ChangeEvent, useEffect, useState } from 'react'
import { apiClient } from '@/api/client'
import { Button } from '@/components/common/Button'
import { LoadingState } from '@/components/common/LoadingState'
import type { APIResponse } from '@/types/api'

type Booking = { id: string; advisor_name: string; advisor_role: string; topic: string; status: string; advisor_note?: string | null; scheduled_at?: string | null; meeting_url?: string | null; created_at?: string }
type Message = { id: string; sender_name: string; body: string }
type DocumentRequest = { id: string; title: string; instructions?: string | null; status: string; documents: { id: string; original_name: string; reviewed: boolean }[] }

type VisibleBooking = Booking & { duplicateCount: number }

function activeBookingKey(booking: Booking) {
  return [booking.advisor_name.trim().toLowerCase(), booking.topic.trim().toLowerCase(), booking.status, booking.scheduled_at ?? 'unscheduled'].join('|')
}

function visibleBookings(bookings: Booking[]): VisibleBooking[] {
  const grouped = new Map<string, VisibleBooking>()
  for (const booking of bookings) {
    const key = activeBookingKey(booking)
    const existing = grouped.get(key)
    if (existing && ['pending', 'accepted'].includes(booking.status)) {
      existing.duplicateCount += 1
      continue
    }
    grouped.set(key, { ...booking, duplicateCount: 0 })
  }
  return [...grouped.values()]
}

export function FounderAppointmentsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]), [loading, setLoading] = useState(true), [selected, setSelected] = useState<Booking | null>(null), [messages, setMessages] = useState<Message[]>([]), [documents, setDocuments] = useState<DocumentRequest[]>([]), [reply, setReply] = useState(''), [notice, setNotice] = useState('')
  const load = () => apiClient.get<APIResponse<Booking[]>>('/human-advisors/booking-requests/mine').then(({ data }) => setBookings(data.data)).catch(() => setNotice('Appointments could not be loaded.')).finally(() => setLoading(false))
  useEffect(() => { void load() }, [])
  useEffect(() => { if (selected) window.setTimeout(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }), 0) }, [selected])
  const open = async (booking: Booking) => { setSelected(booking); const [m, d] = await Promise.all([apiClient.get<APIResponse<Message[]>>(`/human-advisors/booking-requests/${booking.id}/messages`), apiClient.get<APIResponse<DocumentRequest[]>>(`/human-advisors/booking-requests/${booking.id}/document-requests`)]); setMessages(m.data.data); setDocuments(d.data.data) }
  const sendReply = async () => { if (!selected || !reply.trim()) return; const { data } = await apiClient.post<APIResponse<Message>>(`/human-advisors/booking-requests/${selected.id}/messages`, { body: reply }); setMessages((items) => [...items, data.data]); setReply('') }
  const upload = async (requestId: string, event: ChangeEvent<HTMLInputElement>) => { const file = event.target.files?.[0]; if (!file) return; const body = new FormData(); body.append('document', file); try { await apiClient.post(`/human-advisors/document-requests/${requestId}/upload`, body, { headers: { 'Content-Type': 'multipart/form-data' } }); setNotice('Document stored securely for your assigned advisor.'); if (selected) await open(selected) } catch { setNotice('Upload failed. Use a PDF, PNG, or JPEG under 5 MB.') } }
  if (loading) return <LoadingState label="Loading your appointments..." />
  const appointments = visibleBookings(bookings)
  const hiddenDuplicates = bookings.length - appointments.length
  return <div className="mx-auto max-w-6xl space-y-6"><header><p className="page-eyebrow">Founder appointments</p><h1 className="page-title">Your advisor consultations</h1><p className="mt-2 text-slate-600 dark:text-slate-300">Track acceptance, meeting details, advisor messages, and requested documents in one place.</p></header>{notice && <p className="rounded-xl bg-brand-50 p-4 text-sm text-brand-800">{notice}</p>}{hiddenDuplicates > 0 && <p className="rounded-xl bg-amber-50 p-4 text-sm text-amber-900">{hiddenDuplicates} repeated booking {hiddenDuplicates === 1 ? 'entry was' : 'entries were'} grouped with the active appointment. Future duplicate submissions are prevented.</p>}<div className="grid gap-5 md:grid-cols-2">{appointments.map((booking) => <article key={booking.id} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700 capitalize">{booking.status}</span><h2 className="mt-4 text-xl font-bold">{booking.topic}</h2><p className="mt-2 text-sm">{booking.advisor_role}: <strong>{booking.advisor_name}</strong></p>{booking.scheduled_at && <p className="mt-3 text-sm font-bold text-brand-700">{new Date(booking.scheduled_at).toLocaleString()}</p>}{booking.advisor_note && <p className="mt-3 rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800">{booking.advisor_note}</p>}<Button className="mt-5" onClick={() => void open(booking)}>View appointment</Button></article>)}</div>{!appointments.length && <section className="rounded-2xl border border-dashed border-slate-300 p-10 text-center text-slate-500">No advisor appointments yet.</section>}{selected && <section className="rounded-2xl border border-brand-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><div className="flex flex-wrap justify-between gap-3"><h2 className="text-xl font-bold">{selected.topic}</h2>{selected.meeting_url && <a className="font-bold text-brand-700 underline" href={selected.meeting_url} target="_blank" rel="noreferrer">Join online meeting →</a>}</div><div className="mt-6 grid gap-6 lg:grid-cols-2"><section><h3 className="font-bold">Conversation</h3><div className="mt-3 max-h-48 space-y-2 overflow-auto rounded-xl bg-slate-50 p-3 text-sm dark:bg-slate-800">{messages.length ? messages.map((item) => <p key={item.id}><strong>{item.sender_name}:</strong> {item.body}</p>) : <p className="text-slate-500">No messages yet.</p>}</div><div className="mt-3 flex gap-2"><input value={reply} onChange={(e) => setReply(e.target.value)} className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-transparent p-3 text-sm" placeholder="Reply to advisor" /><Button onClick={() => void sendReply()}>Send</Button></div></section><section><h3 className="font-bold">Secure requested documents</h3><div className="mt-3 space-y-3">{documents.length ? documents.map((item) => <div key={item.id} className="rounded-xl bg-slate-50 p-4 text-sm dark:bg-slate-800"><strong>{item.title}</strong><p className="mt-1 text-slate-500">{item.instructions || 'Upload the requested document only if you are comfortable sharing it.'}</p><p className="mt-2 text-xs font-semibold capitalize">{item.status}</p>{item.documents.map((file) => <p key={file.id} className="mt-1 text-xs text-emerald-700">Uploaded: {file.original_name}</p>)}<label className="mt-3 inline-block cursor-pointer rounded-lg border border-brand-300 px-3 py-2 text-xs font-bold text-brand-700">Upload PDF / image<input className="hidden" type="file" accept="application/pdf,image/png,image/jpeg" onChange={(event) => void upload(item.id, event)} /></label></div>) : <p className="text-sm text-slate-500">Your advisor has not requested documents.</p>}</div></section></div><Button className="mt-6" variant="secondary" onClick={() => setSelected(null)}>Close</Button></section>}</div>
}
