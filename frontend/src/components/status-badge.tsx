import type { ItemStatus } from '@/api/generated/model'
import { ITEM_STATUS_LABELS, ITEM_STATUS_TONES } from '@/lib/statuses'
import { cn } from '@/lib/utils'

export function StatusBadge({ status, className }: { status: ItemStatus; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex shrink-0 items-center rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap',
        ITEM_STATUS_TONES[status],
        className,
      )}
    >
      {ITEM_STATUS_LABELS[status]}
    </span>
  )
}
