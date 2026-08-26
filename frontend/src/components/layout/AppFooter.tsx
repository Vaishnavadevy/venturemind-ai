import { Link } from 'react-router-dom'
import { BrandMark } from '@/components/branding/BrandMark'

const groups = [
  { title: 'Product', links: [{ label: 'Founder dashboard', to: '/dashboard' }, { label: 'Startup workspace', to: '/workspace' }, { label: 'AI Advisor', to: '/advisor' }, { label: 'Human advisors', to: '/advisors' }] },
  { title: 'Learning', links: [{ label: 'Founder Knowledge Hub', to: '/knowledge-hub' }, { label: 'Founder guides', to: '/learn' }, { label: 'Market research', to: '/tools' }, { label: 'Templates', to: '/templates' }, { label: 'Free tools', to: '/calculators' }] },
  { title: 'Company', links: [{ label: 'Our methodology', to: '/about' }, { label: 'Explainable AI', to: '/explainable-ai' }, { label: 'Privacy Policy', to: '/privacy' }, { label: 'Terms of Service', to: '/terms' }, { label: 'Contact', to: '/contact' }, { label: 'Frequently asked questions', to: '/faq' }] },
]

export function AppFooter() {
  return <footer id="footer" className="mt-12 border-t border-slate-200 bg-white/85 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85"><div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-[1.4fr_repeat(3,1fr)]"><div><Link className="flex items-center gap-2 text-lg font-bold" to="/"><BrandMark /> <span>VentureMind <span className="text-brand-600">AI</span></span></Link><p className="mt-3 max-w-xs text-sm leading-6 text-slate-500">Evidence-led startup planning, risk analysis, and practical next steps.</p><p className="mt-5 text-xs text-slate-400">Built to support informed startup decisions; outcomes still depend on real evidence, execution, and professional advice where needed.</p></div>{groups.map((group) => <div key={group.title}><h2 className="text-sm font-bold">{group.title}</h2>{group.links.map((link) => <Link key={link.label} className="mt-3 block text-sm text-slate-500 transition hover:text-brand-600" to={link.to}>{link.label}</Link>)}</div>)}</div><div className="border-t border-slate-200 px-4 py-5 text-center text-xs text-slate-500 dark:border-slate-800">© 2026 VentureMind AI</div></footer>
}
