import { useEffect, useId, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router'

/**
 * Lets the phone's back button close an overlay instead of leaving the page behind it.
 *
 * While the overlay is open, it adds a history entry for the same page. Back removes
 * that entry, which closes the overlay; closing it any other way removes the entry too.
 * Returns afterClose, for doing something on closing (navigating, opening another
 * overlay) once the entry is gone, so it doesn't race the history change.
 */
export function useBackToClose(open: boolean, close: () => void) {
  const location = useLocation()
  const navigate = useNavigate()
  const id = useId()
  const ours = (location.state as { overlay?: string } | null)?.overlay === id
  const pushed = useRef(false) // our entry is (or was) in history
  const pending = useRef(false) // a push or back is on its way
  const closeRef = useRef(close)
  useEffect(() => {
    closeRef.current = close
  })

  useEffect(() => {
    if (open && ours) {
      pushed.current = true
      pending.current = false
    } else if (open && !ours) {
      if (pushed.current) {
        // Back was pressed (or something navigated away): close.
        pushed.current = false
        closeRef.current()
      } else if (!pending.current) {
        pending.current = true
        const { pathname, search, hash, state } = location
        navigate({ pathname, search, hash }, { state: { ...(state ?? {}), overlay: id } })
      }
    } else if (!open && ours) {
      // Closed some other way: drop our entry, once.
      if (!pending.current) {
        pending.current = true
        navigate(-1)
      }
    } else {
      pushed.current = false
      pending.current = false
    }
  }, [open, ours, location, navigate, id])

  return (then: () => void) => {
    if (!ours) return then()
    // Wait for the router to see the back step before the next history change.
    window.addEventListener('popstate', () => setTimeout(then), { once: true })
  }
}
