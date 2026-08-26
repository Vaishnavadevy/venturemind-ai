import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/common/Button'

type RapidResult = {
  score: number
  label: string
  summary: string
  strength: string
  nextStep: string
}

function createRapidResult(idea: string, industry: string, market: string): RapidResult {
  const words = idea.trim().split(/\s+/).filter(Boolean).length
  const mentionsCustomer = /customer|user|people|business|student|parent|shop|team|worker|seller|buyer/i.test(idea)
  const mentionsProblem = /help|solve|reduce|improve|make|connect|manage|track|save|predict/i.test(idea)
  const score = Math.min(88, 36 + Math.min(words, 45) + (industry.trim() ? 7 : 0) + (market.trim() ? 6 : 0) + (mentionsCustomer ? 5 : 0) + (mentionsProblem ? 5 : 0))
  const label = score >= 72 ? 'Promising starting point' : score >= 55 ? 'Worth exploring' : 'Needs a clearer hypothesis'
  const missing = !industry.trim() ? 'the industry' : !market.trim() ? 'the first market' : !mentionsCustomer ? 'the target customer' : 'the customer problem'
  return {
    score,
    label,
    summary: `Your idea has enough detail to start a conversation, but its potential depends on evidence from real customers.`,
    strength: mentionsProblem ? 'You describe a possible problem or outcome, which is a useful early signal.' : 'You have a starting concept that can be sharpened with one clear customer problem.',
    nextStep: `Ask five potential customers about ${missing} before deciding what to build.`,
  }
}

export function ValidateLandingPage() {
  const [idea, setIdea] = useState('')
  const [industry, setIndustry] = useState('')
  const [market, setMarket] = useState('')
  const [result, setResult] = useState<RapidResult | null>(null)

  const validate = () => setResult(createRapidResult(idea, industry, market))

  return (
    <div className="-mx-4 -my-8 sm:-mx-6">
      <section className="bg-gradient-to-br from-brand-50 via-white to-accent-50 px-4 py-20 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 sm:px-6">
        <div className="mx-auto max-w-5xl text-center"><p className="text-sm font-bold uppercase tracking-widest text-brand-600">Rapid startup validation</p><h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">Get a clearer next step in seconds.</h1><p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">Describe an idea you are considering. No account, project, or backend connection is required.</p></div>
      </section>

      <section className="px-4 py-16 sm:px-6"><div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <form className="rounded-2xl border border-slate-200 bg-white p-6 shadow-float dark:border-slate-800 dark:bg-slate-900" onSubmit={(event) => { event.preventDefault(); validate() }}><h2 className="text-xl font-bold">Describe your startup idea</h2><label className="sr-only" htmlFor="rapid-idea">Your idea</label><textarea id="rapid-idea" value={idea} onChange={(event) => setIdea(event.target.value)} rows={4} className="mt-4 w-full rounded-xl border border-slate-300 bg-transparent p-3 text-sm dark:border-slate-700" placeholder="Example: A platform that helps small retailers predict stock demand..."/><div className="mt-4 grid gap-3 sm:grid-cols-2"><input value={industry} onChange={(event) => setIndustry(event.target.value)} className="rounded-xl border border-slate-300 bg-transparent p-3 text-sm dark:border-slate-700" placeholder="Industry (optional)"/><input value={market} onChange={(event) => setMarket(event.target.value)} className="rounded-xl border border-slate-300 bg-transparent p-3 text-sm dark:border-slate-700" placeholder="Country or market (optional)"/></div><p className="mt-4 text-xs leading-5 text-slate-500">This is a quick, indicative check based only on the information you enter. It is not a market forecast or a full AI evaluation.</p><Button className="mt-5 w-full" disabled={idea.trim().length < 10} type="submit">Get rapid validation</Button></form>

        <aside className="rounded-2xl border border-slate-200 bg-slate-950 p-6 text-white shadow-float dark:border-slate-800">{result ? <><p className="text-sm font-bold uppercase tracking-widest text-accent-300">Rapid validation — indicative result</p><div className="mt-6 flex items-center gap-5"><div className="grid h-24 w-24 place-items-center rounded-full border-8 border-brand-400 text-center"><strong className="text-3xl">{result.score}</strong><span className="text-xs text-slate-300">/100</span></div><div><h2 className="text-2xl font-bold">{result.label}</h2><p className="mt-1 text-sm text-slate-300">A starting point, not a prediction.</p></div></div><p className="mt-6 leading-7 text-slate-200">{result.summary}</p><div className="mt-5 space-y-4"><div className="rounded-xl bg-white/10 p-4"><p className="text-xs font-bold uppercase tracking-widest text-accent-300">What is working</p><p className="mt-2 text-sm leading-6 text-slate-200">{result.strength}</p></div><div className="rounded-xl bg-white/10 p-4"><p className="text-xs font-bold uppercase tracking-widest text-accent-300">Best next step</p><p className="mt-2 text-sm leading-6 text-slate-200">{result.nextStep}</p></div></div><Link className="mt-6 inline-block text-sm font-bold text-accent-300 hover:underline" to="/idea-generator">Need a different direction? Generate ideas →</Link></> : <div className="flex h-full min-h-[330px] flex-col justify-center"><p className="text-sm font-bold uppercase tracking-widest text-accent-300">Rapid validation — indicative result</p><h2 className="mt-4 text-3xl font-bold">Your quick result will appear here.</h2><p className="mt-4 leading-7 text-slate-300">Write at least one sentence about your idea, then get a simple evidence-focused starting point in seconds.</p></div>}</aside>
      </div></section>
    </div>
  )
}
