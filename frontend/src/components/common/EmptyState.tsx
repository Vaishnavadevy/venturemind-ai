import type { ReactNode } from 'react'

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <section className="surface-card border-dashed p-10 text-center"><div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-brand-50 text-xl text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">+</div><h2 className="mt-4 text-lg font-bold">{title}</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500 dark:text-slate-400">{description}</p>{action && <div className="mt-5">{action}</div>}</section>
}
