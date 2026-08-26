export type UserRole = 'user' | 'founder' | 'admin' | 'legal_advisor' | 'business_mentor' | 'job_applicant' | 'investor'

export interface AuthUser {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_email_verified: boolean
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
  access_token_expires_at: string
  refresh_token_expires_at: string
  user: AuthUser
}
