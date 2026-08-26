import { useEffect, useState } from 'react'
import type { AxiosError } from 'axios'
import { useNavigate } from 'react-router-dom'

import { lifecycleApi, type StartupProfileResponse } from '@/features/lifecycle/lifecycle.api'
import { useAuth } from '@/features/auth/AuthContext'

type Message = { role: 'user' | 'advisor'; content: string }

/** Compact, profile-aware AI Advisor for signed-in founders. */
export function FounderAdvisorChatWidget() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [profiles, setProfiles] = useState<StartupProfileResponse[]>([])
  const [profileId, setProfileId] = useState('')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [error, setError] = useState('')
  const [thinking, setThinking] = useState(false)

  const availableForFounder = Boolean(user && !['admin', 'legal_advisor', 'business_mentor'].includes(user.role))

  useEffect(() => {
    if (!open || !availableForFounder || profiles.length) return
    lifecycleApi.listProfiles()
      .then((items) => {
        setProfiles(items)
        setProfileId(items[0]?.id ?? '')
      })
      .catch(() => setError('Your saved startup profile could not be loaded. Refresh and sign in again if needed.'))
  }, [availableForFounder, open, profiles.length])

  useEffect(() => {
    const openAdvisor = () => setOpen(true)
    window.addEventListener('venturemind:open-advisor-chat', openAdvisor)
    return () => window.removeEventListener('venturemind:open-advisor-chat', openAdvisor)
  }, [])

  if (!availableForFounder) return null

  const ask = async () => {
    if (!profileId || !question.trim()) return
    const submitted = question.trim()
    setQuestion('')
    setError('')
    setThinking(true)
    setMessages((items) => [...items, { role: 'user', content: submitted }])
    try {
      // Prefer the profile-aware local Ollama route. It deliberately avoids the
      // optional chat-history tables, so a partially migrated local database
      // cannot block a founder from receiving real AI guidance.
      const reply = await lifecycleApi.askAdvisorQuick(profileId, submitted)
      setMessages((items) => [...items, { role: 'advisor', content: reply.response }])
    } catch (caughtError) {
      const axiosError = caughtError as AxiosError<{ detail?: string; message?: string }>
      if (!axiosError.response) setError('The AI service is temporarily unavailable. Confirm the FastAPI backend is running, then try again.')
      else setError(axiosError.response.data?.detail ?? axiosError.response.data?.message ?? 'The AI Advisor could not respond. Please try again.')
    } finally {
      setThinking(false)
    }
  }

  return <div className="fixed bottom-5 right-5 z-50">
    {open && <section className="mb-3 w-[min(27rem,calc(100vw-2.5rem))] overflow-hidden rounded-3xl border border-violet-200 bg-white shadow-2xl shadow-slate-950/20">
      <header className="bg-slate-950 px-5 py-4 text-white"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-widest text-violet-300">AI business advisor</p><h2 className="mt-1 text-lg font-bold">Ask VentureMind</h2></div><button className="rounded-lg px-2 py-1 text-slate-300 hover:bg-white/10 hover:text-white" onClick={() => setOpen(false)} aria-label="Close AI advisor">×</button></div><p className="mt-2 text-xs leading-5 text-slate-300">Your selected startup profile is used to provide context-aware guidance.</p><div className="mt-3 flex gap-2"><button type="button" onClick={() => navigate(-1)} className="rounded-lg border border-white/15 px-2.5 py-1.5 text-xs font-bold text-violet-100 hover:bg-white/10">← Back</button><button type="button" onClick={() => navigate('/')} className="rounded-lg border border-white/15 px-2.5 py-1.5 text-xs font-bold text-violet-100 hover:bg-white/10">⌂ Home</button></div></header>
      <div className="max-h-72 space-y-3 overflow-y-auto p-4">{!profiles.length && !error ? <p className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">Loading your startup context…</p> : null}{profiles.length > 1 && <label className="block text-xs font-bold text-slate-600">Startup context<select value={profileId} onChange={(event) => { setProfileId(event.target.value); setMessages([]) }} className="mt-1 w-full rounded-lg border border-slate-200 bg-white p-2 text-sm font-normal">{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.business_name}</option>)}</select></label>}{messages.map((message, index) => <article key={`${message.role}-${index}`} className={`whitespace-pre-wrap rounded-2xl p-3 text-sm leading-6 ${message.role === 'user' ? 'ml-8 bg-violet-600 text-white' : 'mr-4 bg-violet-50 text-slate-800'}`}><p className="mb-1 text-xs font-bold uppercase tracking-wider opacity-75">{message.role === 'user' ? 'You' : 'VentureMind'}</p>{message.content}</article>)}{!messages.length && profiles.length > 0 && <p className="rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">Ask about pricing, target customers, marketing, risk reduction, finance, or launch planning.</p>}{error && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}</div>
      <div className="border-t border-slate-100 p-4"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} placeholder={profiles.length ? 'Ask about your startup…' : 'Create a startup profile first…'} disabled={!profiles.length || thinking} className="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-100 disabled:bg-slate-50" /><button disabled={!profileId || !question.trim() || thinking} onClick={() => void ask()} className="mt-3 w-full rounded-xl bg-violet-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60">{thinking ? 'Thinking…' : 'Send message'}</button></div>
    </section>}
    <button onClick={() => setOpen((value) => !value)} className="flex items-center gap-2 rounded-full bg-violet-600 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-violet-600/30 transition hover:bg-violet-700" aria-expanded={open}><span className="grid h-6 w-6 place-items-center rounded-full bg-white/15 text-lg">✦</span>{open ? 'Close assistant' : 'Ask VentureMind'}</button>
  </div>
}
