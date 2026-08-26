export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return <div className="surface-card grid min-h-48 place-items-center p-8 text-center"><div><span className="mx-auto block h-8 w-8 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600 dark:border-slate-800 dark:border-t-brand-400" /><p className="mt-4 text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p></div></div>
}
