import { STATUS_LABELS, STATUS_TONES, type Status } from '@/lib/statuses'
import { cn } from '@/lib/utils'

export function StatusBadge({ status, className }: { status: Status; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex shrink-0 items-center rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap',
        STATUS_TONES[status],
        className,
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}
