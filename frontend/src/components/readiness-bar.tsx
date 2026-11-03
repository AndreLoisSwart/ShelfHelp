import type { Readiness } from '@/api/generated/model'
import { cn } from '@/lib/utils'

type Props = {
  readiness: Readiness
  /** Also mention nice-to-have items, e.g. in a project header. */
  detailed?: boolean
  className?: string
}

/** Required items on hand, out of all required. Hidden when nothing is required. */
export function ReadinessBar({ readiness, detailed, className }: Props) {
  const { ready, required, nice_ready, nice_to_have } = readiness
  if (required === 0) return null
  const complete = ready === required
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div
        role="progressbar"
        aria-label="Readiness"
        aria-valuemin={0}
        aria-valuemax={required}
        aria-valuenow={ready}
        className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"
      >
        <div
          className={cn('h-full rounded-full', complete ? 'bg-status-green' : 'bg-primary')}
          style={{ width: `${(ready / required) * 100}%` }}
        />
      </div>
      <span className="shrink-0 text-xs text-muted-foreground">
        {ready} of {required} ready
        {detailed && nice_to_have > 0 && ` · ${nice_ready} of ${nice_to_have} nice to have`}
      </span>
    </div>
  )
}
