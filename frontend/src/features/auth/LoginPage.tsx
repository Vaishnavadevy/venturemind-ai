import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { AuthForm, FormError, SubmitButton } from './AuthForm'
import { useAuth } from './AuthContext'

const loginSchema = z.object({ email: z.string().email('Enter a valid email address.'), password: z.string().min(1, 'Enter your password.') })
type LoginValues = z.infer<typeof loginSchema>

export function LoginPage() {
  const { login } = useAuth(); const navigate = useNavigate(); const location = useLocation(); const [error, setError] = useState<string | null>(null)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) })
  const onSubmit = async (values: LoginValues) => { try { setError(null); const signedInUser = await login(values.email, values.password); const defaultRoute = signedInUser.role === 'admin' ? '/admin' : signedInUser.role === 'legal_advisor' || signedInUser.role === 'business_mentor' ? '/advisor-dashboard' : '/dashboard'; navigate(location.state?.from?.pathname ?? defaultRoute, { replace: true }) } catch { setError('Unable to sign in. Check your credentials and try again.') } }
  return <AuthForm title="Welcome back" footer={<>New to VentureMind? <Link className="font-semibold text-brand-600 hover:underline" to="/register">Create an account</Link></>}><form onSubmit={handleSubmit(onSubmit)} noValidate><label className="mt-6 block text-sm font-medium">Email<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" type="email" autoComplete="email" {...register('email')} /></label>{errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}<label className="mt-4 block text-sm font-medium">Password<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" type="password" autoComplete="current-password" {...register('password')} /></label>{errors.password && <p className="text-sm text-red-600">{errors.password.message}</p>}<div className="mt-2 text-right"><Link className="text-sm font-semibold text-brand-600 hover:underline" to="/forgot-password">Forgot password?</Link></div><FormError message={error}/><SubmitButton isSubmitting={isSubmitting}>Sign in</SubmitButton><p className="mt-5 text-center text-xs leading-5 text-slate-500">By continuing, you agree to the <Link className="font-semibold text-brand-600 hover:underline" to="/terms">Terms of Service</Link> and acknowledge the <Link className="font-semibold text-brand-600 hover:underline" to="/privacy">Privacy Policy</Link>.</p></form></AuthForm>
}
