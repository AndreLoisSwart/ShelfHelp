import { useState } from 'react'

// Behind Ingress the app shares Home Assistant's origin, and so its localStorage.
const PREFIX = 'shelf-help:'

/** A per-device preference kept in localStorage, limited to the allowed values. */
export function usePersistentState<T extends string>(
  key: string,
  initial: T,
  allowed: readonly T[],
) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(PREFIX + key)
      return allowed.includes(stored as T) ? (stored as T) : initial
    } catch {
      return initial
    }
  })
  const set = (next: T) => {
    setValue(next)
    try {
      localStorage.setItem(PREFIX + key, next)
    } catch {
      // Storage can be unavailable, e.g. in private browsing. Keep it for this visit.
    }
  }
  return [value, set] as const
}
