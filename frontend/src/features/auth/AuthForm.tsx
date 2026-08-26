import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/common/Button'

export function AuthForm({ title, children, footer }: { title: string; children: ReactNode; footer: ReactNode }) {
  return <section className="mx-auto max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-card dark:border-slate-800 dark:bg-slate-900"><Link to="/" className="text-sm font-bold text-brand-600">VentureMind AI</Link><h1 className="mt-5 text-2xl font-bold">{title}</h1>{children}<div className="mt-6 text-center text-sm text-slate-600 dark:text-slate-300">{footer}</div></section>
}

export function FormError({ message }: { message: string | null }) {
  return message ? <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">{message}</p> : null
}

export function SubmitButton({ isSubmitting, children }: { isSubmitting: boolean; children: ReactNode }) {
  return <Button className="mt-6 w-full" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Please wait…' : children}</Button>
}
