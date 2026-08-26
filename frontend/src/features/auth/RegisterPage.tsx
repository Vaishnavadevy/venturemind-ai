import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { AuthForm, FormError, SubmitButton } from './AuthForm'
import { useAuth } from './AuthContext'
import { apiErrorMessage } from '@/api/errors'

const registerSchema = z.object({ fullName: z.string().min(2, 'Enter your name.'), email: z.string().email('Enter a valid email address.'), password: z.string().min(12, 'Use at least 12 characters.') })
type RegisterValues = z.infer<typeof registerSchema>

export function RegisterPage() {
  const { register: createAccount } = useAuth(); const navigate = useNavigate(); const [error, setError] = useState<string | null>(null)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) })
  const onSubmit = async (values: RegisterValues) => { try { setError(null); await createAccount(values.fullName, values.email, values.password); navigate('/login', { state: { registered: true } }) } catch (requestError) { setError(apiErrorMessage(requestError, 'Unable to create the account. Check that the backend and database are running.')) } }
  return <AuthForm title="Create your account" footer={<>Already have an account? <Link className="font-semibold text-brand-600 hover:underline" to="/login">Sign in</Link></>}><form onSubmit={handleSubmit(onSubmit)} noValidate><label className="mt-6 block text-sm font-medium">Full name<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" autoComplete="name" {...register('fullName')} /></label>{errors.fullName && <p className="text-sm text-red-600">{errors.fullName.message}</p>}<label className="mt-4 block text-sm font-medium">Email<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" type="email" autoComplete="email" {...register('email')} /></label>{errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}<label className="mt-4 block text-sm font-medium">Password<input className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 dark:border-slate-700" type="password" autoComplete="new-password" {...register('password')} /></label>{errors.password && <p className="text-sm text-red-600">{errors.password.message}</p>}<FormError message={error}/><SubmitButton isSubmitting={isSubmitting}>Create account</SubmitButton><p className="mt-5 text-center text-xs leading-5 text-slate-500">By creating an account, you agree to the <Link className="font-semibold text-brand-600 hover:underline" to="/terms">Terms of Service</Link> and <Link className="font-semibold text-brand-600 hover:underline" to="/privacy">Privacy Policy</Link>.</p></form></AuthForm>
}
