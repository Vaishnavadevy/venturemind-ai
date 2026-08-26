import { useEffect, useMemo, useState } from 'react'
import type { AxiosError } from 'axios'

import { Button } from '@/components/common/Button'
import { LoadingState } from '@/components/common/LoadingState'
import { lifecycleApi, type StartupProfileResponse } from '@/features/lifecycle/lifecycle.api'

type Message = { role: 'user' | 'advisor'; content: string; mode?: string }

function locationFor(profile: StartupProfileResponse) {
  return [profile.city, profile.district, profile.country].filter((item, index, items) => Boolean(item) && items.indexOf(item) === index).join(', ') || 'Location not added'
}

export function BusinessAdvisorPage() {
  const [profiles, setProfiles] = useState<StartupProfileResponse[]>([])
  const [profileId, setProfileId] = useState('')
  const [question, setQuestion] = useState('What should I validate first before launching?')
  const [messages, setMessages] = useState<Message[]>([])
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    lifecycleApi.listProfiles()
      .then((items) => { setProfiles(items); setProfileId(items[0]?.id ?? '') })
      .catch(() => setError('Your startup profiles could not be loaded. Sign in again, then confirm the backend and database are running.'))
      .finally(() => setLoading(false))
  }, [])

  const selectedProfile = useMemo(() => profiles.find((profile) => profile.id === profileId) ?? null, [profileId, profiles])

  const ask = async () => {
    if (!profileId || !question.trim()) return
    const submitted = question.trim()
    setSending(true)
    setError('')
    setMessages((items) => [...items, { role: 'user', content: submitted }])
    setQuestion('')
    try {
      const reply = await lifecycleApi.askAdvisor(profileId, submitted, conversationId)
      setConversationId(reply.conversation_id)
      setMessages((items) => [...items, { role: 'advisor', content: reply.response, mode: reply.mode }])
    } catch (caughtError) {
      const error = caughtError as AxiosError<{ detail?: string; message?: string }>
      const status = error.response?.status
      const detail = error.response?.data?.detail ?? error.response?.data?.message
      if (status === 401) setError('Your sign-in session has expired. Sign in again and retry your question.')
      else if (status && status >= 500) setError(`The advisor service returned error ${status}${detail ? `: ${detail}` : '. Check the backend terminal, then try again.'}`)
      else if (!error.response) setError('The advisor API could not be reached. Confirm the FastAPI backend is running on port 8000.')
      else setError(detail ?? 'The advisor could not respond. Please try again.')
    } finally {
      setSending(false)
    }
  }

  if (loading) return <LoadingState label="Loading your AI advisor..." />
  if (!profiles.length) return <div className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-8 shadow-card dark:border-slate-800 dark:bg-slate-900"><p className="text-sm font-bold uppercase tracking-widest text-brand-600">AI business advisor</p><h1 className="mt-2 text-3xl font-bold">Create a startup profile first</h1><p className="mt-3 text-slate-600 dark:text-slate-300">The advisor uses a saved business profile to give context-aware guidance.</p></div>

  return <div className="mx-auto max-w-5xl space-y-5">
    <header className="rounded-3xl bg-slate-950 px-6 py-7 text-white shadow-card sm:px-8"><p className="text-sm font-bold uppercase tracking-widest text-accent-300">AI business advisor</p><h1 className="mt-2 text-3xl font-bold">Practical guidance for your startup</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">Ask a clear business question. VentureMind uses the selected saved profile, risk assessment, and financial plan when they are available. Guidance is decision support—not legal, financial, or investment advice.</p></header>

    <section className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]"><div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card dark:border-slate-800 dark:bg-slate-900"><label className="text-sm font-bold">Startup context<select value={profileId} onChange={(event) => { setProfileId(event.target.value); setConversationId(undefined); setMessages([]) }} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700">{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.business_name} · {locationFor(profile)}</option>)}</select></label>{selectedProfile && <div className="mt-5 rounded-xl bg-brand-50 p-4 text-sm dark:bg-brand-500/10"><p className="font-bold text-brand-800 dark:text-brand-200">Context currently used</p><dl className="mt-3 space-y-2 text-slate-700 dark:text-slate-200"><div><dt className="text-xs font-semibold text-slate-500">Offer</dt><dd>{selectedProfile.description || 'Add a business description in the workspace.'}</dd></div><div><dt className="text-xs font-semibold text-slate-500">Customers</dt><dd>{selectedProfile.target_customers || 'Add target customers in the workspace.'}</dd></div><div><dt className="text-xs font-semibold text-slate-500">Location</dt><dd>{locationFor(selectedProfile)}</dd></div><div><dt className="text-xs font-semibold text-slate-500">Goal</dt><dd>{selectedProfile.business_goals || 'Add your business goal in the workspace.'}</dd></div></dl></div>}</div>
      <section className="rounded-2xl bg-slate-950 p-5 text-white shadow-card"><div className="min-h-[300px] space-y-4">{messages.length === 0 ? <div className="grid min-h-[300px] place-items-center text-center"><div><p className="text-lg font-bold">What would you like to decide?</p><p className="mt-2 max-w-md text-sm leading-6 text-slate-300">Try questions about customer validation, pricing, finance, marketing, risk reduction, or launch planning.</p></div></div> : messages.map((message, index) => <article key={`${message.role}-${index}`} className={`max-w-[94%] whitespace-pre-wrap rounded-2xl p-4 text-sm leading-6 ${message.role === 'user' ? 'ml-auto bg-brand-600 text-white' : 'bg-white/10 text-slate-100'}`}><p className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-300">{message.role === 'advisor' ? (message.mode === 'ollama' ? 'Local AI guidance · Ollama' : message.mode === 'gemini' ? 'Gemini guidance' : 'Structured guidance') : 'You'}</p>{message.content}</article>)}</div><div className="mt-5 border-t border-white/10 pt-5"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} placeholder="Ask a question about this startup..." className="w-full rounded-xl border border-slate-700 bg-slate-900 p-3 text-sm text-white placeholder:text-slate-400" /><div className="mt-3 flex flex-wrap items-center justify-between gap-3"><p className="text-xs text-slate-400">Selected startup context is used for every response.</p><Button disabled={sending || !question.trim()} onClick={() => void ask()}>{sending ? 'Thinking...' : 'Send message'}</Button></div>{error && <p className="mt-3 text-sm text-red-300">{error}</p>}</div></section></section>
  </div>
}
