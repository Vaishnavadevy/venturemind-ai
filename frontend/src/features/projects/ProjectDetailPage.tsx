import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { LoadingState } from '@/components/common/LoadingState'
import { projectApi, type ProjectSummary } from './project.api'

export function ProjectDetailPage() {
  const { projectId } = useParams(); const navigate = useNavigate(); const [project, setProject] = useState<ProjectSummary | null>(null); const [error, setError] = useState(false); const [archiving, setArchiving] = useState(false)
  useEffect(() => { if (projectId) projectApi.get(projectId).then(setProject).catch(() => setError(true)) }, [projectId])
  if (error) return <p className="rounded-xl bg-red-50 p-5 text-red-700">Project unavailable. <Link className="font-bold underline" to="/dashboard">Return to dashboard</Link></p>
  if (!project) return <LoadingState label="Loading project..." />
  const archive = async () => { if (!projectId || !confirm('Archive this project?')) return; setArchiving(true); try { await projectApi.archive(projectId); navigate('/dashboard') } finally { setArchiving(false) } }
  return <div className="mx-auto max-w-3xl space-y-6"><header><p className="text-sm font-bold text-brand-600">Startup project</p><h1 className="mt-1 text-3xl font-bold">{project.name}</h1><p className="mt-2 text-slate-600 dark:text-slate-300">{project.industry} · {project.development_stage.toUpperCase()} · {project.status}</p><div className="mt-5 flex gap-3"><Link className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white" to={`/projects/new?versionOf=${project.id}`}>Create a new version</Link>{project.status !== 'archived' && <button className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold" disabled={archiving} onClick={() => void archive()}>{archiving ? 'Archiving…' : 'Archive project'}</button>}</div></header><section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><h2 className="text-xl font-bold">Latest evaluation</h2>{project.latest_evaluation_id ? <><p className="mt-3 text-sm text-slate-600 dark:text-slate-300">The latest assessment scored <strong>{project.latest_score ?? '—'}</strong> out of 100.</p><Link className="mt-5 inline-block rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white" to={`/projects/${project.id}/evaluations/${project.latest_evaluation_id}`}>Open evaluation</Link></> : <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">An evaluation has not been completed yet.</p>}</section></div>
}
