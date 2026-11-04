import { apiUrl } from '../lib/base-path'

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
  ) {
    super(`API request failed with status ${status}`)
  }
}

// Used by every generated API call. Prefixes the base path so requests work behind
// HA Ingress, and throws on error responses so TanStack Query treats them as errors.
export const apiFetch = async <T>(url: string, options: RequestInit): Promise<T> => {
  const res = await fetch(apiUrl(url), options)
  const text = await res.text()
  const body = text ? JSON.parse(text) : undefined
  if (!res.ok) throw new ApiError(res.status, body)
  return body as T
}

// Picked up by orval as the error type of every generated hook. It must be generic.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export type ErrorType<_Error> = ApiError

/** A message fit to show the user, e.g. in a toast. */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const detail = (error.body as { detail?: unknown } | undefined)?.detail
    if (typeof detail === 'string') return detail
    // FastAPI validation errors: a list, each with a message. Show the first one.
    if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') {
      return detail[0].msg.replace(/^Value error, /, '')
    }
    if (error.status === 422) return 'Some of the values are not valid'
    return `Something went wrong (${error.status})`
  }
  return 'Could not reach Shelf-help'
}
