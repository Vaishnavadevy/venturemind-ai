import { Component, type ErrorInfo, type ReactNode } from 'react'

interface State { error: Error | null }

/** Prevents an unexpected page error from becoming a blank white screen. */
export class AppErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State { return { error } }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Keep diagnostics available during local development without exposing server data.
    console.error('VentureMind page error', error, info)
  }

  render() {
    if (this.state.error) return <main className="mx-auto max-w-3xl p-8"><section className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-900"><p className="text-sm font-bold uppercase tracking-wider">Page error</p><h1 className="mt-2 text-2xl font-bold">This screen could not be displayed.</h1><p className="mt-3 text-sm">{this.state.error.message || 'Unexpected interface error.'}</p><button className="mt-5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white" onClick={() => this.setState({ error: null })}>Try again</button></section></main>
    return this.props.children
  }
}
