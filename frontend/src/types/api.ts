export interface APIResponse<T> {
  data: T
  message?: string
}

export interface APIError {
  error: {
    code: string
    message: string
    fields?: Record<string, string[]>
  }
}
