import { useEffect, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'

import { LoadingState } from '@/components/common/LoadingState'
import { Button } from '@/components/common/Button'
import { apiClient } from '@/api/client'
import { reportApi } from '@/features/reports/report.api'
import type { APIResponse } from '@/types/api'

type Recommendation = { metric?: string; recommendation?: string; title?: string; detail?: string }
type Evaluation = {
  overall_confidence_score: number | null
  scores: Array<{ metric_key: string; score: number; reasoning: string; positive_factors: string[]; improvement_suggestions: string[] }>
  swot_analysis: Record<string, string[]> | null
  business_model_canvas: Record<string, string> | null
  market_analysis: Record<string, unknown> | null
  risk_analysis: { level?: string; risk_resilience_score?: number; note?: string } | null
  roadmap: Array<{ phase: string; milestone: string; outcome?: string }> | null
  recommendations: Recommendation[] | null
}

const title = (key: unknown) => String(key ?? 'Recommendation').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
function Card({ heading, children }: { heading: string; children: ReactNode }) { return <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><h2 className="text-xl font-bold">{heading}</h2>{children}</section> }

export function EvaluationResultsPage() {
  const { projectId, evaluationId } = useParams()
  const [result, setResult] = useState<Evaluation | null>(null)
  const [error, setError] = useState('')
  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState('')

  useEffect(() => {
    if (!projectId || !evaluationId) return
    apiClient.get<APIResponse<Evaluation>>(`/projects/${projectId}/evaluations/${evaluationId}`)
      .then(({ data }) => setResult(data.data))
      .catch((requestError) => setError(requestError?.response?.data?.error?.message || 'The evaluation could not be loaded. Confirm that you are signed in as the project owner and that the backend is running.'))
  }, [projectId, evaluationId])

  const downloadReport = async () => {
    if (!projectId || !evaluationId) return
    setReportLoading(true); setReportError('')
    try { await reportApi.generate(projectId, evaluationId) } catch { setReportError('Could not generate the PDF. Confirm that the backend is running, then try again.') } finally { setReportLoading(false) }
  }

  if (error) return <p className="rounded-xl bg-red-50 p-5 text-red-700">Evaluation unavailable: {error} <Link className="font-bold underline" to="/dashboard">Return to dashboard</Link></p>
  if (!result) return <LoadingState label="Loading your explainable evaluation..." />

  const scores = Array.isArray(result.scores) ? result.scores : []
  const swot = result.swot_analysis && typeof result.swot_analysis === 'object' ? result.swot_analysis : {}
  const canvas = result.business_model_canvas && typeof result.business_model_canvas === 'object' ? result.business_model_canvas : {}
  const market = result.market_analysis && typeof result.market_analysis === 'object' ? result.market_analysis : {}
  const risk = result.risk_analysis ?? {}
  const recommendations = Array.isArray(result.recommendations) ? result.recommendations : []
  const roadmap = Array.isArray(result.roadmap) ? result.roadmap : []

  return <div className="mx-auto max-w-7xl space-y-6">
    <header className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-bold text-brand-600">Evaluation complete</p><h1 className="mt-1 text-3xl font-bold">Your startup assessment</h1><p className="mt-2 text-slate-600 dark:text-slate-300">Scores measure submitted evidence quality—not a prediction of success.</p></div><div><Button disabled={reportLoading} onClick={() => void downloadReport()}>{reportLoading ? 'Generating PDF...' : 'Download PDF report'}</Button>{reportError && <p className="mt-2 max-w-xs text-xs text-red-700">{reportError}</p>}</div></header>
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]"><Card heading="Overall confidence"><p className="mt-6 text-6xl font-bold text-brand-600">{result.overall_confidence_score ?? '—'}</p><p className="mt-1 text-slate-500">out of 100</p></Card><Card heading="Explainable scorecards"><div className="grid gap-3 md:grid-cols-2">{scores.map((score) => <article key={score.metric_key} className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800"><div className="flex justify-between"><h3 className="font-bold">{title(score.metric_key)}</h3><strong className="text-brand-600">{score.score}</strong></div><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{score.reasoning}</p><p className="mt-3 text-sm font-semibold text-emerald-700">{score.positive_factors?.[0] ?? 'No positive factor recorded.'}</p><p className="mt-2 text-sm font-semibold text-amber-700">{score.improvement_suggestions?.[0] ?? 'Continue collecting evidence.'}</p></article>)}</div></Card></div>
    <div className="grid gap-6 xl:grid-cols-2"><Card heading="SWOT analysis"><div className="mt-4 grid gap-3 sm:grid-cols-2">{Object.entries(swot).map(([key, items]) => <div key={key} className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800"><h3 className="font-bold">{title(key)}</h3>{(Array.isArray(items) ? items : [String(items)]).map((item) => <p key={item} className="mt-2 text-sm text-slate-600 dark:text-slate-300">- {item}</p>)}</div>)}</div></Card><Card heading="Risk analysis"><p className="mt-5 text-3xl font-bold capitalize">{risk.level ?? 'No'} risk context</p><div className="mt-4 h-3 rounded-full bg-slate-100"><div className="h-full rounded-full bg-brand-600" style={{ width: `${risk.risk_resilience_score ?? 0}%` }} /></div><p className="mt-4 text-sm text-slate-600 dark:text-slate-300">{risk.note ?? 'No saved risk explanation is available.'}</p></Card></div>
    <Card heading="Business model canvas"><div className="mt-4 grid gap-3 md:grid-cols-3">{Object.entries(canvas).map(([key, value]) => <article key={key} className="rounded-xl border border-slate-200 p-4 dark:border-slate-800"><h3 className="font-bold">{title(key)}</h3><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{String(value)}</p></article>)}</div></Card>
    <div className="grid gap-6 xl:grid-cols-2"><Card heading="Market analysis">{Object.entries(market).map(([key, value]) => <div key={key} className="mt-4"><h3 className="font-bold">{title(key)}</h3><p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{String(value)}</p></div>)}</Card><Card heading="Recommendations">{recommendations.map((item, index) => <div key={item.metric ?? item.title ?? index} className="mt-4 flex gap-3"><strong className="text-brand-600">0{index + 1}</strong><p className="text-sm text-slate-600 dark:text-slate-300"><span className="font-bold">{title(item.metric ?? item.title)}: </span>{item.recommendation ?? item.detail ?? 'No recommendation detail recorded.'}</p></div>)}</Card></div>
    <Card heading="Startup roadmap"><div className="mt-4 grid gap-4 md:grid-cols-5">{roadmap.map((item, index) => <article key={`${item.phase}-${index}`}><strong className="text-3xl text-brand-200">0{index + 1}</strong><h3 className="mt-2 font-bold">{item.phase}</h3><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{item.milestone}</p><p className="mt-2 text-xs font-bold text-brand-600">{item.outcome ?? 'Next milestone'}</p></article>)}</div></Card>
  </div>
}
