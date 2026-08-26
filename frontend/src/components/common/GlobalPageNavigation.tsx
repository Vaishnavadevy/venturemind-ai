import { useLocation, useNavigate } from 'react-router-dom'

export function GlobalPageNavigation() {
  const navigate = useNavigate()
  const location = useLocation()
  // Keep Home free of a redundant navigation control. All dashboards retain this
  // helper because users can otherwise become stranded after opening a deep link.
  if (location.pathname === '/') return null

  const previous = () => {
    if (window.history.length > 1) navigate(-1)
    else navigate('/')
  }

  return <nav aria-label="Page navigation" className="fixed bottom-5 left-5 z-40 flex items-center gap-1 rounded-2xl border border-violet-400/30 bg-slate-950/95 p-1.5 text-white shadow-[0_18px_45px_-16px_rgba(49,46,129,0.65)] backdrop-blur dark:border-violet-300/25"><button type="button" onClick={previous} className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold text-violet-100 transition hover:bg-violet-500 hover:text-white" aria-label="Go to previous page" title="Previous page"><span className="text-base leading-none">←</span><span>Back</span></button><span className="h-5 w-px bg-white/15" /><button type="button" onClick={() => navigate('/')} className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold text-violet-100 transition hover:bg-violet-500 hover:text-white" aria-label="Go to home page" title="Home"><span className="text-sm leading-none">⌂</span><span>Home</span></button></nav>
}
