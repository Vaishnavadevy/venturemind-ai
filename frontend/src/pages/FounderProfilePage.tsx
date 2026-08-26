import { useEffect, useState } from 'react'
import { Button } from '@/components/common/Button'
import { useAuth } from '@/features/auth/AuthContext'

type PersonalProfile = { fullName: string; dateOfBirth: string; nicPassport: string; tin: string; phone: string; address: string; avatar: string }
const key = 'venturemind.founder-personal-profile'
const avatars = ['🌱', '🚀', '💡', '🧭']
const masked = (value: string) => value ? '••••' + value.slice(-4) : 'Not added'

export function FounderProfilePage() {
  const { user } = useAuth()
  const [profile, setProfile] = useState<PersonalProfile>({ fullName: user?.full_name ?? '', dateOfBirth: '', nicPassport: '', tin: '', phone: '', address: '', avatar: '🌱' })
  const [saved, setSaved] = useState(false)
  useEffect(() => { try { const existing = JSON.parse(localStorage.getItem(key) ?? '{}') as Partial<PersonalProfile>; setProfile((current) => ({ ...current, ...existing, fullName: existing.fullName || user?.full_name || current.fullName })) } catch { /* start fresh */ } }, [user?.full_name])
  const save = () => { localStorage.setItem(key, JSON.stringify(profile)); setSaved(true) }
  const field = (label: string, name: keyof PersonalProfile, type = 'text') => <label className="text-sm font-semibold">{label}<input type={type} value={profile[name]} onChange={(e) => setProfile({ ...profile, [name]: e.target.value })} className="mt-2 w-full rounded-xl border border-slate-300 bg-white p-3 font-normal" /></label>
  return <main className="mx-auto max-w-5xl space-y-6"><header className="rounded-3xl bg-gradient-to-br from-slate-950 via-indigo-950 to-violet-900 p-7 text-white"><p className="text-sm font-bold uppercase tracking-widest text-violet-200">Founder account</p><div className="mt-3 flex flex-wrap items-center gap-4"><span className="grid h-16 w-16 place-items-center rounded-3xl bg-white/10 text-3xl shadow-inner">{profile.avatar}</span><div><h1 className="text-3xl font-extrabold">{profile.fullName || 'Your personal profile'}</h1><p className="mt-1 text-indigo-100">Keep your personal account details separate from your startup business profile.</p></div></div></header>
    <section className="grid gap-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:grid-cols-2"><div className="md:col-span-2"><p className="text-sm font-bold uppercase tracking-widest text-violet-700">Profile icon</p><div className="mt-3 flex flex-wrap gap-3">{avatars.map((avatar) => <button key={avatar} onClick={() => setProfile({ ...profile, avatar })} className={'grid h-14 w-14 place-items-center rounded-2xl text-2xl ' + (profile.avatar === avatar ? 'bg-violet-600 ring-4 ring-violet-100' : 'bg-slate-100 hover:bg-violet-50')}>{avatar}</button>)}</div></div>{field('Full name', 'fullName')}{field('Date of birth', 'dateOfBirth', 'date')}{field('NIC or passport reference', 'nicPassport')}{field('Personal TIN reference', 'tin')}{field('Phone number', 'phone')}{field('Home address', 'address')}<div className="md:col-span-2 flex flex-wrap items-center gap-4"><Button onClick={save}>Save personal profile</Button>{saved && <p className="text-sm font-semibold text-emerald-700">Saved on this device for this academic project.</p>}</div></section>
    <section className="rounded-3xl border border-amber-200 bg-amber-50 p-6"><h2 className="font-bold text-amber-950">Privacy note</h2><p className="mt-2 text-sm leading-6 text-amber-900">Identity references are masked in the account preview and stored only in this browser for the local academic demonstration. A production system would encrypt them on the server with strict access controls.</p><div className="mt-4 grid gap-3 text-sm sm:grid-cols-2"><p><strong>NIC / passport:</strong> {masked(profile.nicPassport)}</p><p><strong>Personal TIN:</strong> {masked(profile.tin)}</p></div></section>
  </main>
}
