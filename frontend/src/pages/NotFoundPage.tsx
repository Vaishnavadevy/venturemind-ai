import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return <section className="py-20 text-center"><p className="text-sm font-semibold text-brand-600">404</p><h1 className="mt-2 text-3xl font-bold">Page not found</h1><Link className="mt-6 inline-block text-brand-600 hover:underline" to="/">Return home</Link></section>
}
