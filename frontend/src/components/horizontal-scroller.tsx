import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useCallback, useEffect, useRef, useState, type MouseEvent, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type Props = {
  children: ReactNode
  className?: string
  onClickCapture?: (e: MouseEvent) => void
}

/**
 * A row that scrolls sideways, showing that it does: a fade and an arrow on each edge
 * with more beyond it. Desktop scrollbars are often hidden until used (and sit at the
 * bottom of a tall row); phones swipe, so the hints are for wider screens only.
 */
export function HorizontalScroller({ children, className, onClickCapture }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const [more, setMore] = useState({ left: false, right: false })

  const update = useCallback(() => {
    const el = ref.current
    if (!el) return
    const left = el.scrollLeft > 1
    const right = el.scrollLeft + el.clientWidth < el.scrollWidth - 1
    setMore((m) => (m.left === left && m.right === right ? m : { left, right }))
  }, [])

  // What fits changes with the row's own width (the window, the page going wide) and
  // its children's (columns shown, hidden or resized), so watch both.
  const observer = useRef<ResizeObserver | null>(null)
  useEffect(() => {
    observer.current = new ResizeObserver(update)
    return () => observer.current?.disconnect()
  }, [update])
  useEffect(() => {
    const el = ref.current
    if (!el || !observer.current) return
    for (const target of [el, ...el.children]) observer.current.observe(target)
    update()
  })

  /** About one child (e.g. a board column) at a time. */
  const step = (direction: 1 | -1) => {
    const el = ref.current
    if (!el) return
    const child = el.firstElementChild as HTMLElement | null
    const gap = parseFloat(getComputedStyle(el).columnGap) || 0
    const distance = child ? child.offsetWidth + gap : el.clientWidth * 0.8
    el.scrollBy({ left: direction * distance, behavior: 'smooth' })
  }

  const edge = (side: 'left' | 'right') => (
    <>
      <div
        aria-hidden
        className={cn(
          'pointer-events-none absolute inset-y-0 hidden w-16 from-background to-transparent md:block',
          side === 'left' ? 'left-0 bg-gradient-to-r' : 'right-0 bg-gradient-to-l',
        )}
      />
      <Button
        variant="outline"
        size="icon-sm"
        className={cn(
          'absolute top-1/2 hidden -translate-y-1/2 rounded-full shadow-sm md:flex',
          side === 'left' ? 'left-1' : 'right-1',
        )}
        onClick={() => step(side === 'left' ? -1 : 1)}
        aria-label={side === 'left' ? 'Scroll left' : 'Scroll right'}
      >
        {side === 'left' ? <ChevronLeft /> : <ChevronRight />}
      </Button>
    </>
  )

  return (
    <div className="relative">
      <div ref={ref} onScroll={update} onClickCapture={onClickCapture} className={className}>
        {children}
      </div>
      {more.left && edge('left')}
      {more.right && edge('right')}
    </div>
  )
}
