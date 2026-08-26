import { useState } from 'react'
import { Link } from 'react-router-dom'
import { PublicOllamaChatWidget } from '@/components/chat/PublicOllamaChatWidget'

const features = [
  ['Explainable scoring', 'See the evidence behind every confidence score, including strengths, risks, and practical ways to improve.'],
  ['Complete business plan', 'Turn an early concept into a SWOT analysis, business model canvas, roadmap, and financial assumptions.'],
  ['Investor-ready clarity', 'Identify funding readiness, critical milestones, and the questions investors are likely to ask.'],
]

const steps = [
  ['01', 'Describe your venture', 'Share the problem, target market, solution, and business model in a guided workspace.'],
  ['02', 'Get an explainable evaluation', 'VentureMind combines structured evaluation factors with AI-powered business analysis.'],
  ['03', 'Build with confidence', 'Use your prioritized recommendations, roadmap, and downloadable report to take the next step.'],
]

const testimonials = [
  ['“The score was useful, but the explanation was the real breakthrough. It showed exactly what to validate before building.”', 'Maya Fernando', 'Fintech founder'],
  ['“We transformed a scattered idea into a focused MVP plan in one working session.”', 'Dilan Perera', 'Product lead'],
  ['“The report gave our early team a shared, evidence-led starting point for customer interviews.”', 'Nethmi Silva', 'Healthtech founder'],
]

const faqs = [
  ['Are the scores random?', 'No. VentureMind uses documented, weighted evaluation factors. AI enriches the written analysis, but numeric scores come from deterministic scoring logic.'],
  ['Is VentureMind a substitute for market research?', 'No. It helps you structure and prioritize research. You should still validate assumptions with real customers, market data, and qualified advisers.'],
  ['Who can use VentureMind?', 'Anyone exploring a startup idea—from first-time founders to incubators and product teams—can create a project and receive an evaluation.'],
]

function SectionHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <div className="mx-auto max-w-2xl text-center"><p className="text-sm font-bold uppercase tracking-widest text-brand-600">{eyebrow}</p><h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">{title}</h2><p className="mt-4 text-base leading-7 text-slate-600 dark:text-slate-300">{description}</p></div>
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false)
  return <article className="border-b border-slate-200 py-5 dark:border-slate-800"><button className="flex w-full items-center justify-between gap-6 text-left font-semibold" aria-expanded={open} onClick={() => setOpen((current) => !current)}><span>{question}</span><span className="text-xl text-brand-600">{open ? '−' : '+'}</span></button>{open && <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">{answer}</p>}</article>
}

export function LandingPage() {
  return <div className="-mx-4 -my-8 sm:-mx-6">
    <section className="overflow-hidden bg-gradient-to-br from-brand-50 via-white to-indigo-50 px-4 py-20 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 sm:px-6 sm:py-28">
      <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
        <div><p className="inline-flex rounded-full bg-brand-100 px-3 py-1 text-sm font-semibold text-brand-700 dark:bg-brand-500/10 dark:text-brand-500">Explainable AI for ambitious founders</p><h1 className="mt-6 max-w-3xl text-5xl font-bold tracking-tight sm:text-6xl">Move your startup from idea to a <span className="text-brand-600">clear launch plan.</span></h1><p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">Organise your business profile, understand risks, plan money, prepare registration steps, and decide what to do next—before investing months of effort.</p><div className="mt-9 flex flex-wrap gap-3"><Link to="/register" className="rounded-lg bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition hover:bg-brand-700">Start your startup plan</Link><a href="#how-it-works" className="rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-800 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">See how it works</a></div><p className="mt-5 text-sm text-slate-500 dark:text-slate-400">One guided journey. Clear assumptions. Practical next steps.</p></div>
        <div className="overflow-hidden rounded-2xl border border-white/80 bg-white/85 shadow-2xl shadow-brand-950/10 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90"><img className="h-64 w-full object-cover object-center" src="/images/venturemind-founder-hero.png" alt="Founder using VentureMind to plan a startup" /><div className="p-5"><div className="flex items-center justify-between gap-3"><div><p className="text-sm font-bold">From founder inputs to a clear next step</p><p className="mt-1 text-xs text-slate-500">Scores appear only after a founder saves evidence in the workspace.</p></div><span className="rounded-full bg-violet-100 px-2.5 py-1 text-xs font-bold text-violet-800">Explainable workflow</span></div><div className="mt-5 grid grid-cols-3 gap-2 text-center text-xs font-bold"><div className="rounded-xl bg-violet-50 px-2 py-3 text-violet-900">1. Profile & evidence</div><div className="rounded-xl bg-sky-50 px-2 py-3 text-sky-900">2. Risk & finance</div><div className="rounded-xl bg-emerald-50 px-2 py-3 text-emerald-900">3. Next actions</div></div></div></div>
      </div>
    </section>

    <section id="features" className="px-4 py-20 sm:px-6"><SectionHeading eyebrow="Built for decisions" title="More than a score." description="VentureMind gives you the structured thinking and explainable analysis needed to move an idea forward responsibly." /><div className="mx-auto mt-12 grid max-w-7xl gap-6 md:grid-cols-3">{features.map(([title, description], index) => <article key={title} className="rounded-2xl border border-slate-200 bg-white p-7 shadow-card transition hover:-translate-y-1 dark:border-slate-800 dark:bg-slate-900"><span className="grid h-10 w-10 place-items-center rounded-lg bg-brand-100 font-bold text-brand-700 dark:bg-brand-500/10 dark:text-brand-400">0{index + 1}</span><h3 className="mt-5 text-xl font-bold">{title}</h3><p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{description}</p></article>)}</div></section>

    <section className="bg-slate-950 px-4 py-20 text-white sm:px-6"><div className="mx-auto grid max-w-7xl items-center gap-10 lg:grid-cols-[1fr_0.85fr]"><div><p className="text-sm font-bold uppercase tracking-widest text-accent-500">Free founder tool</p><h2 className="mt-3 text-3xl font-bold sm:text-4xl">Turn your experience into a startup direction worth exploring.</h2><p className="mt-4 max-w-xl leading-7 text-slate-300">Choose an industry, target customer, skills, and market. VentureMind creates editable concept drafts with a revenue path, key risk, and a practical MVP starting point.</p><div className="mt-7 flex flex-wrap gap-3"><Link className="rounded-lg bg-white px-5 py-3 text-sm font-bold text-brand-700 hover:bg-brand-50" to="/idea-generator">Generate startup ideas</Link><Link className="rounded-lg border border-slate-700 px-5 py-3 text-sm font-bold text-white hover:bg-slate-900" to="/tools">Explore founder tools</Link></div></div><div className="rounded-2xl border border-brand-400/30 bg-gradient-to-br from-brand-600 to-indigo-950 p-6 shadow-float"><p className="text-xs font-bold uppercase tracking-widest text-brand-100">Idea generator preview</p><h3 className="mt-4 text-2xl font-bold">ClarityFlow</h3><p className="mt-2 text-brand-100">A focused digital workflow for independent cafés to make better sustainable retail decisions.</p><div className="mt-5 grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-white/10 p-3"><p className="text-xs text-brand-100">Revenue model</p><p className="mt-1 text-sm font-bold">Subscription starter tier</p></div><div className="rounded-xl bg-white/10 p-3"><p className="text-xs text-brand-100">MVP</p><p className="mt-1 text-sm font-bold">Interview 10 target users</p></div></div></div></div></section>

    <section id="how-it-works" className="bg-slate-100 px-4 py-20 dark:bg-slate-900/60 sm:px-6"><SectionHeading eyebrow="A focused workflow" title="From idea to action in three steps." description="Spend less time assembling blank templates and more time testing the assumptions that matter." /><div className="mx-auto mt-12 grid max-w-7xl gap-8 md:grid-cols-3">{steps.map(([number, title, description]) => <article key={number} className="relative"><span className="text-5xl font-black text-brand-200 dark:text-brand-500/20">{number}</span><h3 className="mt-3 text-xl font-bold">{title}</h3><p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{description}</p></article>)}</div></section>

    <section className="px-4 py-20 sm:px-6"><SectionHeading eyebrow="Founder stories" title="Clarity makes momentum possible." description="Early-stage builders use VentureMind to sharpen their thinking before their next important decision." /><div className="mx-auto mt-12 grid max-w-7xl gap-6 md:grid-cols-3">{testimonials.map(([quote, name, role]) => <figure key={name} className="rounded-2xl bg-brand-600 p-7 text-white"><blockquote className="text-lg leading-8">{quote}</blockquote><figcaption className="mt-8"><p className="font-bold">{name}</p><p className="text-sm text-brand-100">{role}</p></figcaption></figure>)}</div></section>

    <section id="faq" className="bg-white px-4 py-20 dark:bg-slate-950 sm:px-6"><div className="mx-auto max-w-4xl"><SectionHeading eyebrow="FAQ" title="Questions, answered." description="A transparent starting point for your venture evaluation." /><div className="mt-10">{faqs.map(([question, answer]) => <FAQItem key={question} question={question} answer={answer} />)}</div></div></section>

    <section className="bg-brand-700 px-4 py-16 text-center text-white sm:px-6"><h2 className="text-3xl font-bold">Ready to evaluate what you’re building?</h2><p className="mx-auto mt-3 max-w-xl text-brand-100">Bring your idea. Leave with a clearer plan to validate, build, and grow.</p><Link to="/register" className="mt-7 inline-block rounded-lg bg-white px-5 py-3 text-sm font-semibold text-brand-700 transition hover:bg-brand-50">Create your free account</Link></section>
    <PublicOllamaChatWidget />
  </div>
}
