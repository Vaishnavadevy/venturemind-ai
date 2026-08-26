import { useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/common/Button'
import { lifecycleApi, type StartupProfileResponse } from '@/features/lifecycle/lifecycle.api'
import { operationsApi, type OperationsSnapshot } from '@/features/operations/operations.api'

const emptySnapshot: OperationsSnapshot = { employees: [], tasks: [], announcements: [], attendance: [], leave_requests: [] }

export function BusinessOperationsPage() {
  const [profiles, setProfiles] = useState<StartupProfileResponse[]>([])
  const [profileId, setProfileId] = useState('')
  const [data, setData] = useState<OperationsSnapshot>(emptySnapshot)
  const [employeeName, setEmployeeName] = useState('')
  const [employeeTitle, setEmployeeTitle] = useState('')
  const [taskTitle, setTaskTitle] = useState('')
  const [announcement, setAnnouncement] = useState('')
  const [leaveEmployeeId, setLeaveEmployeeId] = useState('')
  const [leaveStart, setLeaveStart] = useState(new Date().toISOString().slice(0, 10))
  const [leaveEnd, setLeaveEnd] = useState(new Date().toISOString().slice(0, 10))
  const [leaveReason, setLeaveReason] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const selectedProfile = useMemo(() => profiles.find((profile) => profile.id === profileId), [profiles, profileId])
  const reload = async (id = profileId) => { if (id) setData(await operationsApi.getSnapshot(id)) }

  useEffect(() => {
    const load = async () => {
      try {
        const items = await lifecycleApi.listProfiles()
        setProfiles(items)
        if (items[0]) { setProfileId(items[0].id); setData(await operationsApi.getSnapshot(items[0].id)) }
      } catch { setError('Could not load business operations. Ensure the backend is running and sign in again.') }
      finally { setLoading(false) }
    }
    void load()
  }, [])

  const perform = async (action: () => Promise<void>) => {
    setSaving(true); setError('')
    try { await action() } catch { setError('Could not save this change. Please check your backend connection and try again.') } finally { setSaving(false) }
  }

  if (loading) return <p className="mx-auto max-w-6xl py-12 text-slate-500">Loading business operations…</p>

  return <div className="mx-auto max-w-6xl space-y-7">
    <header className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-bold uppercase tracking-widest text-brand-600">Business operations</p><h1 className="mt-2 text-3xl font-bold">Run your early team in one workspace.</h1><p className="mt-2 text-slate-600 dark:text-slate-300">Employees, tasks, attendance, leave requests and announcements are saved securely to your startup profile.</p></div>{profiles.length > 1 && <select value={profileId} onChange={(event) => { setProfileId(event.target.value); void reload(event.target.value) }} className="rounded-lg border border-slate-300 bg-white p-2 dark:border-slate-700 dark:bg-slate-900">{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.business_name}</option>)}</select>}</header>
    {!selectedProfile && <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-950">Create and save a founder profile in the Workspace before using Business Operations.</div>}
    {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
    {selectedProfile && <div className="grid gap-6 lg:grid-cols-2">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><h2 className="text-xl font-bold">Employees and attendance</h2><div className="mt-4 grid gap-2 sm:grid-cols-3"><input value={employeeName} onChange={e => setEmployeeName(e.target.value)} placeholder="Employee name" className="rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"/><input value={employeeTitle} onChange={e => setEmployeeTitle(e.target.value)} placeholder="Job title (optional)" className="rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"/><Button disabled={saving} onClick={() => void perform(async () => { if (!employeeName.trim()) return; await operationsApi.addEmployee(profileId, { full_name: employeeName.trim(), job_title: employeeTitle.trim() || null }); setEmployeeName(''); setEmployeeTitle(''); await reload() })}>Add employee</Button></div><div className="mt-4 space-y-2">{data.employees.length === 0 ? <p className="text-sm text-slate-500">No employees added yet.</p> : data.employees.map((employee) => <div key={employee.id} className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800"><strong>{employee.full_name}</strong><span className="ml-2 text-sm text-slate-500">{employee.job_title || 'Team member'}</span><div className="mt-2 flex flex-wrap gap-2"><span className="mr-1 text-xs text-slate-500">Today:</span>{(['present', 'absent', 'leave'] as const).map((status) => <button key={status} disabled={saving} onClick={() => void perform(async () => { await operationsApi.recordAttendance(profileId, employee.id, status); await reload() })} className="rounded-md border border-slate-300 px-2 py-1 text-xs capitalize hover:border-brand-500 dark:border-slate-600">{status}</button>)}</div></div>)}</div></section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><h2 className="text-xl font-bold">Tasks</h2><div className="mt-4 flex gap-2"><input value={taskTitle} onChange={e => setTaskTitle(e.target.value)} placeholder="New operational task" className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"/><Button disabled={saving} onClick={() => void perform(async () => { if (!taskTitle.trim()) return; await operationsApi.addTask(profileId, { title: taskTitle.trim() }); setTaskTitle(''); await reload() })}>Add task</Button></div><div className="mt-4 space-y-2">{data.tasks.length === 0 ? <p className="text-sm text-slate-500">No tasks added yet.</p> : data.tasks.map((task) => <label key={task.id} className="flex cursor-pointer gap-2 rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800"><input type="checkbox" checked={task.status === 'done'} disabled={saving} onChange={() => void perform(async () => { await operationsApi.updateTask(profileId, task.id, task.status === 'done' ? 'todo' : 'done'); await reload() })}/><span className={task.status === 'done' ? 'line-through text-slate-400' : ''}>{task.title}</span></label>)}</div></section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><h2 className="text-xl font-bold">Leave requests</h2><div className="mt-4 grid gap-2 sm:grid-cols-2"><select value={leaveEmployeeId} onChange={e => setLeaveEmployeeId(e.target.value)} className="rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"><option value="">Select employee</option>{data.employees.map(employee => <option key={employee.id} value={employee.id}>{employee.full_name}</option>)}</select><input type="text" value={leaveReason} onChange={e => setLeaveReason(e.target.value)} placeholder="Reason (optional)" className="rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"/><input type="date" value={leaveStart} onChange={e => setLeaveStart(e.target.value)} className="rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"/><input type="date" value={leaveEnd} onChange={e => setLeaveEnd(e.target.value)} className="rounded-lg border border-slate-300 bg-transparent p-2 dark:border-slate-700"/></div><Button className="mt-3" disabled={saving || !leaveEmployeeId} onClick={() => void perform(async () => { await operationsApi.requestLeave(profileId, { employee_id: leaveEmployeeId, start_date: leaveStart, end_date: leaveEnd, reason: leaveReason || null }); setLeaveReason(''); await reload() })}>Request leave</Button><div className="mt-4 space-y-2">{data.leave_requests.map(request => <p key={request.id} className="rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800">{data.employees.find(e => e.id === request.employee_id)?.full_name || 'Employee'} · {request.start_date} to {request.end_date} · <span className="capitalize">{request.status}</span></p>)}</div></section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"><h2 className="text-xl font-bold">Announcements</h2><textarea value={announcement} onChange={e => setAnnouncement(e.target.value)} rows={4} placeholder="Share an update with the team" className="mt-4 w-full rounded-lg border border-slate-300 bg-transparent p-3 dark:border-slate-700"/><Button className="mt-3" disabled={saving} onClick={() => void perform(async () => { if (!announcement.trim()) return; await operationsApi.addAnnouncement(profileId, announcement.trim()); setAnnouncement(''); await reload() })}>Post announcement</Button><div className="mt-4 space-y-2">{data.announcements.length === 0 ? <p className="text-sm text-slate-500">No announcements posted yet.</p> : data.announcements.map(item => <p key={item.id} className="rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800">{item.message}</p>)}</div></section>
    </div>}
  </div>
}
