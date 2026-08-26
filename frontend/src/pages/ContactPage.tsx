import { useState, type FormEvent } from 'react'
import { apiClient } from '@/api/client'
import { Button } from '@/components/common/Button'

export function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', message: '' })
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setStatus('sending')
    try {
      await apiClient.post('/public-feedback', { ...form, category: 'Contact message' })
      setStatus('sent')
      setForm({ name: '', email: '', message: '' })
    } catch {
      setStatus('error')
    }
  }

  return <div className="-mx-4 -my-8 sm:-mx-6">
    <section className="bg-slate-950 px-4 py-20 text-center text-white sm:px-6">
      <p className="text-sm font-bold uppercase tracking-widest text-accent-300">Contact</p>
      <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">Help us make VentureMind more useful.</h1>
      <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-300">Share feedback, a feature idea, or a question about VentureMind.</p>
    </section>
    <section className="px-4 py-20 sm:px-6">
      <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[0.8fr_1.2fr]">
        <div><p className="text-sm font-bold uppercase tracking-widest text-brand-600">Project contact</p><h2 className="mt-3 text-3xl font-bold">Your feedback matters.</h2><p className="mt-4 leading-7 text-slate-600 dark:text-slate-300">Messages are recorded in the VentureMind feedback queue for an administrator to review. This form does not send external email yet.</p></div>
        <form className="rounded-2xl border border-slate-200 bg-white p-6 shadow-float dark:border-slate-800 dark:bg-slate-900" onSubmit={(event) => void submit(event)}>
          <label className="text-sm font-semibold">Name<input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700" /></label>
          <label className="mt-4 block text-sm font-semibold">Email<input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700" /></label>
          <label className="mt-4 block text-sm font-semibold">Message<textarea required minLength={10} rows={4} value={form.message} onChange={(event) => setForm({ ...form, message: event.target.value })} className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700" /></label>
          {status === 'sent' && <p className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">Thank you—your feedback is now in the administrator feedback queue.</p>}
          {status === 'error' && <p className="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-800">Your message could not be sent. Confirm that the backend is running, then try again.</p>}
          <Button className="mt-5 w-full" type="submit" disabled={status === 'sending'}>{status === 'sending' ? 'Sending…' : 'Send message'}</Button>
        </form>
      </div>
    </section>
  </div>
}
