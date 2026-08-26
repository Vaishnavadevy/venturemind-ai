import { describe, expect, it } from 'vitest'
import { apiErrorMessage } from './errors'

describe('apiErrorMessage', () => {
  it('uses the server error message when one is provided', () => {
    const error = { isAxiosError: true, response: { data: { error: { code: 'validation_error', message: 'Request validation failed.' } } } }
    expect(apiErrorMessage(error, 'Fallback')).toBe('Request validation failed.')
  })

  it('uses the fallback for non-API errors', () => {
    expect(apiErrorMessage(new Error('offline'), 'Connection failed.')).toBe('Connection failed.')
  })
})
