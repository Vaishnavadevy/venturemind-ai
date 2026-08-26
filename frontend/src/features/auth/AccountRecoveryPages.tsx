import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { AuthForm, FormError, SubmitButton } from './AuthForm'
import { authApi } from './auth.api'

export function VerifyEmailPage() {
  const [params] = useSearchParams(); const [message, setMessage] = useState('Verifying your email address...'); const token = params.get('token')
  useEffect(() => { if (!token) { setMessage('This verification link is invalid.'); return } authApi.verifyEmail(token).then(() => setMessage('Your email is verified. You can now sign in.')).catch(() => setMessage('This verification link is invalid or has expired.')) }, [token])
  return <AuthForm title="Email verification" footer={<Link className="font-semibold text-brand-600 hover:underline" to="/login">Go to sign in</Link>}><p className="mt-6 text-sm text-slate-600 dark:text-slate-300">{message}</p></AuthForm>
}

export function ForgotPasswordPage() {
  const [email, setEmail] = useState(''); const [message, setMessage] = useState<string | null>(null); const [error, setError] = useState<string | null>(null); const [loading, setLoading] = useState(false)
  const submit = async (event: FormEvent) => { event.preventDefault(); setLoading(true); setError(null); try { const { data } = await authApi.forgotPassword(email); setMessage(data.message ?? 'Check your email for password reset instructions.') } catch { setError('We could not request a password reset. Please try again.') } finally { setLoading(false) } }
  return <AuthForm title="Reset your password" footer={<Link className="font-semibold text-brand-600 hover:underline" to="/login">Back to sign in</Link>}>{message ? <p className="mt-6 text-sm text-emerald-700">{message}</p> : <form className="mt-6" onSubmit={submit}><label className="block text-sm font-medium">Email<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label><FormError message={error}/><SubmitButton isSubmitting={loading}>Send reset link</SubmitButton></form>}</AuthForm>
}

export function ResetPasswordPage() {
  const [params] = useSearchParams(); const navigate = useNavigate(); const [password, setPassword] = useState(''); const [error, setError] = useState<string | null>(null); const [loading, setLoading] = useState(false); const token = params.get('token')
  const submit = async (event: FormEvent) => { event.preventDefault(); if (!token) { setError('This reset link is invalid.'); return } if (password.length < 12) { setError('Use at least 12 characters.'); return } setLoading(true); setError(null); try { await authApi.resetPassword(token, password); navigate('/login', { state: { reset: true } }) } catch { setError('This reset link is invalid or has expired.') } finally { setLoading(false) } }
  return <AuthForm title="Choose a new password" footer={<Link className="font-semibold text-brand-600 hover:underline" to="/login">Back to sign in</Link>}><form className="mt-6" onSubmit={submit}><label className="block text-sm font-medium">New password<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" type="password" autoComplete="new-password" required value={password} onChange={(event) => setPassword(event.target.value)} /></label><FormError message={error}/><SubmitButton isSubmitting={loading}>Update password</SubmitButton></form></AuthForm>
}
