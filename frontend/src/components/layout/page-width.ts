import { createContext, useContext, useEffect } from 'react'

export const PageWidthContext = createContext<(wide: boolean) => void>(() => {})

/** Lets a page use the window's full width instead of the reading width, e.g. the
 * projects board, whose columns need the room. Reverts when the page goes away. */
export function useWidePage(wide = true) {
  const setWide = useContext(PageWidthContext)
  useEffect(() => {
    setWide(wide)
    return () => setWide(false)
  }, [setWide, wide])
}
