import { useState } from 'react'
import { Link } from 'react-router-dom'

const faqs = [
  ['Is rapid validation a real market prediction?', 'No. It is a short, indicative check based only on the information you enter. It is designed to suggest a useful next research step, not predict success.'],
  ['Do I need an account to use the free tools?', 'No. You can use the Startup Idea Generator and Rapid Validation as a guest.'],
  ['How is a full evaluation different?', 'A full evaluation is intended to combine structured startup information with documented scoring factors, risks, business analysis, and a report when the backend workspace is enabled.'],
  ['Are VentureMind scores random?', 'No. Full workspace scores are derived from documented factors in your saved startup profile and the evidence you provide. The public website does not show a real score before you create a profile and complete an analysis.'],
  ['Why does VentureMind ask for my business profile first?', 'Risk, finance, competitor, and recommendation features need your business category, target customers, location, budget, and goals. This prevents generic advice from being presented as personalised analysis.'],
  ['Can I use VentureMind for a business in Sri Lanka?', 'Yes. The platform includes an educational Sri Lanka registration guide with official external links. It does not submit applications to government systems or replace a qualified legal advisor.'],
  ['Can I speak with a real legal advisor or business mentor?', 'Yes, where approved advisor profiles are available. You can browse advisors, request an appointment, receive updates, and share requested documents through the platform workflow.'],
  ['Is my business information public?', 'No. Your saved startup workspace is account-scoped. You choose whether to send information to a human advisor as part of a consultation request.'],
  ['Can I download a report?', 'After a saved startup evaluation is complete, the dashboard can generate reports containing the available evaluation, risks, recommendations, and planning information.'],
  ['How do subscriptions and payments work?', 'Explorer tools are free. Founder and Team plans are priced in LKR, but live checkout requires a configured payment provider, server-side verification, and a secure callback before any payment is accepted.'],
  ['Can I cancel or change a paid plan?', 'Subscription cancellation and plan changes will be available only after the live payment and subscription service is enabled. Until then, paid-plan access is handled as a request, not an automatic charge.'],
  ['Will VentureMind replace customer research?', 'No. It helps you prepare better questions and identify assumptions. Customer conversations and real market evidence remain essential.'],
  ['What should I do if a page says the backend is unavailable?', 'Confirm that MySQL and the FastAPI backend are running, then sign in again. The public learning tools can still be explored without backend data.'],
]

export function FaqPage() {
  const [open, setOpen] = useState<number | null>(0)
  return <div className="-mx-4 -my-8 sm:-mx-6"><section className="bg-gradient-to-br from-brand-50 via-white to-accent-50 px-4 py-20 text-center dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 sm:px-6"><p className="text-sm font-bold uppercase tracking-widest text-brand-600">Frequently asked questions</p><h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">Answers for thoughtful founders.</h1><p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">What VentureMind does, what it does not do, and how to use it responsibly.</p></section><section className="px-4 py-20 sm:px-6"><div className="mx-auto max-w-3xl space-y-3">{faqs.map(([question, answer], index) => <article key={question} className="rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"><button className="flex w-full items-center justify-between gap-4 p-5 text-left font-bold" onClick={() => setOpen(open === index ? null : index)} aria-expanded={open === index}><span>{question}</span><span className="text-brand-600">{open === index ? '−' : '+'}</span></button>{open === index && <p className="border-t border-slate-100 px-5 py-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:text-slate-300">{answer}</p>}</article>)}</div><p className="mt-10 text-center text-sm text-slate-600 dark:text-slate-300">Still have a question? <Link className="font-bold text-brand-600 hover:underline" to="/contact">Contact us</Link>.</p></section></div>
}
