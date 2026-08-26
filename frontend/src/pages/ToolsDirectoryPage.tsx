import { Link } from 'react-router-dom'

type Tool = {
  title: string
  description: string
  category: string
  status: 'Available now' | 'Coming soon'
  to?: string
}

const tools: Tool[] = [
  { title: 'Startup Idea Generator', description: 'Generate input-driven startup directions from your industry, target customer, skills, and market.', category: 'Discovery', status: 'Available now', to: '/idea-generator' },
  { title: 'Startup Idea Validation', description: 'Assess a real idea with explainable scores, structured risks, and practical next actions.', category: 'Validation', status: 'Available now', to: '/validate' },
  { title: 'Founder Calculators', description: 'Estimate costs, break-even sales, and cash runway using transparent planning formulas.', category: 'Finance', status: 'Available now', to: '/calculators' },
  { title: 'Startup Stories', description: 'Read concise success and failure stories with direct links to their documented sources.', category: 'Learning', status: 'Available now', to: '/stories' },
  { title: 'Startup Books', description: 'Find curated startup reading with direct links to official book and publisher pages.', category: 'Learning', status: 'Available now', to: '/books' },
  { title: 'Competitor Snapshot', description: 'Organise comparable products, strengths, gaps, and your potential differentiation.', category: 'Research', status: 'Coming soon' },
  { title: 'Pricing Experiment Planner', description: 'Map an early pricing assumption to a small customer test before committing to a model.', category: 'Strategy', status: 'Coming soon' },
  { title: 'MVP Scope Builder', description: 'Turn an opportunity into a smallest-possible testable product scope.', category: 'Product', status: 'Coming soon' },
  { title: 'Funding Readiness Checklist', description: 'Review the evidence, traction, and narrative investors expect at your current stage.', category: 'Funding', status: 'Coming soon' },
]

const calculatorLinks = [
  ['Startup Cost', '/calculators/startup-cost'], ['Break-Even', '/calculators/break-even'], ['Runway', '/calculators/runway'], ['ROI', '/calculators/roi'], ['CAC', '/calculators/cac'], ['LTV', '/calculators/ltv'], ['Market Size', '/calculators/market-size'], ['Funding', '/calculators/funding'], ['Equity Dilution', '/calculators/equity-dilution'], ['Startup Valuation', '/calculators/valuation'],
]

export function ToolsDirectoryPage() {
  return (
    <div className="-mx-4 -my-8 sm:-mx-6">
      <section className="bg-gradient-to-br from-brand-50 via-white to-accent-50 px-4 py-20 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 sm:px-6">
        <div className="mx-auto max-w-5xl text-center"><p className="text-sm font-bold uppercase tracking-widest text-brand-600">Free founder tools</p><h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">Useful tools for the decisions before the build.</h1><p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">Start with an idea, investigate your assumptions, and move toward an evidence-backed next step.</p></div>
      </section>

      <section className="px-4 py-20 sm:px-6"><div className="mx-auto max-w-7xl"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-sm font-bold uppercase tracking-widest text-brand-600">Tool library</p><h2 className="mt-3 text-3xl font-bold">Choose a focused starting point.</h2></div><p className="max-w-md text-sm leading-6 text-slate-500 dark:text-slate-400">Available tools use your inputs to create a practical starting point. They are not a substitute for customer research or professional advice.</p></div><div className="mt-9 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{tools.map((tool) => <article key={tool.title} className="flex min-h-[260px] flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><div className="flex items-center justify-between gap-3"><span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">{tool.category}</span><span className={`text-xs font-bold ${tool.status === 'Available now' ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>{tool.status}</span></div><h3 className="mt-5 text-xl font-bold">{tool.title}</h3><p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{tool.description}</p>{tool.to ? <Link className="mt-auto pt-6 text-sm font-bold text-brand-600 hover:underline" to={tool.to}>Open tool →</Link> : <span className="mt-auto pt-6 text-sm font-semibold text-slate-400">Planned for a later phase</span>}</article>)}</div></div></section>

      <section className="bg-slate-100 px-4 py-20 dark:bg-slate-900/60 sm:px-6"><div className="mx-auto max-w-7xl"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-sm font-bold uppercase tracking-widest text-brand-600">All calculators</p><h2 className="mt-3 text-3xl font-bold">Open a calculator directly.</h2></div><Link className="text-sm font-bold text-brand-600 hover:underline" to="/calculators">View calculator directory →</Link></div><div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{calculatorLinks.map(([label, to]) => <Link key={to} className="rounded-xl border border-slate-200 bg-white px-4 py-4 text-sm font-bold text-slate-700 shadow-card hover:border-brand-300 hover:text-brand-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200" to={to}>{label} <span className="text-brand-600">→</span></Link>)}</div></div></section>

      <section className="bg-slate-950 px-4 py-16 text-white sm:px-6"><div className="mx-auto flex max-w-5xl flex-col justify-between gap-6 md:flex-row md:items-center"><div><p className="text-sm font-bold uppercase tracking-widest text-accent-300">Start with one question</p><h2 className="mt-2 text-3xl font-bold">What is the riskiest assumption in your startup idea?</h2></div><Link className="shrink-0 rounded-lg bg-white px-5 py-3 text-sm font-bold text-brand-700 hover:bg-brand-50" to="/validate">Validate my idea</Link></div></section>
    </div>
  )
}
