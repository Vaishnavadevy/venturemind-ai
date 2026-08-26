import { useState } from 'react'
import type { AxiosError } from 'axios'

import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'

type Reply = { response: string; mode: string; notice: string }

/** A deliberately general, no-profile assistant for the public landing page. */
export function PublicOllamaChatWidget() {
  const [open, setOpen] = useState(false)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState('')
  const [thinking, setThinking] = useState(false)

  const ask = async () => {
    const trimmed = question.trim()
    if (!trimmed) return
    setThinking(true)
    setError('')
    setAnswer('')
    try {
      const { data } = await apiClient.post<APIResponse<Reply>>('/public-advisor', { question: trimmed }, { timeout: 130_000 })
      setAnswer(data.data.response)
    } catch (caughtError) {
      const error = caughtError as AxiosError<{ detail?: string; message?: string }>
      setError(error.response?.data?.detail ?? 'The local AI could not respond. Confirm Ollama is running, then try again.')
    } finally {
      setThinking(false)
    }
  }

  return <div className="fixed bottom-5 right-5 z-50">
    {open && <section className="mb-3 w-[min(24rem,calc(100vw-2.5rem))] overflow-hidden rounded-3xl border border-violet-200 bg-white shadow-2xl shadow-slate-950/20">
      <header className="bg-slate-950 px-5 py-4 text-white"><div className="flex items-start justify-between gap-3"><h2 className="text-lg font-bold">Ask VentureMind</h2><button className="rounded-lg px-2 py-1 text-slate-300 hover:bg-white/10 hover:text-white" onClick={() => setOpen(false)} aria-label="Close chatbot">×</button></div><p className="mt-2 text-xs leading-5 text-slate-300">General startup guidance only. Your question is processed locally and is not saved as a startup profile.</p></header>
      <div className="max-h-72 overflow-y-auto p-4">{answer ? <div className="whitespace-pre-wrap rounded-2xl bg-violet-50 p-4 text-sm leading-6 text-slate-800">{answer}</div> : <p className="rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">Ask about validating an idea, pricing, finding customers, MVP scope, or preparing to launch.</p>}{error && <p className="mt-3 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}</div>
      <div className="border-t border-slate-100 p-4"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} maxLength={800} placeholder="For example: How can I test demand for a café idea?" className="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-100" /><button disabled={thinking || !question.trim()} onClick={() => void ask()} className="mt-3 w-full rounded-xl bg-violet-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60">{thinking ? 'Thinking with local AI…' : 'Ask VentureMind'}</button></div>
    </section>}
    <button onClick={() => setOpen((value) => !value)} className="flex items-center gap-2 rounded-full bg-violet-600 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-violet-600/30 transition hover:bg-violet-700" aria-expanded={open}><span className="grid h-6 w-6 place-items-center rounded-full bg-white/15 text-lg">✦</span>{open ? 'Close assistant' : 'Ask VentureMind'}</button>
  </div>
}
