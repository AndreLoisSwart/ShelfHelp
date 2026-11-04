import { createContext, useContext } from 'react'

export const QuickAddContext = createContext<() => void>(() => {})

/** Opens the quick-add overlay from anywhere inside QuickAddProvider. */
export function useQuickAdd() {
  return useContext(QuickAddContext)
}
