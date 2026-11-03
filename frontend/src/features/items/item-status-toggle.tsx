import type { ItemStatus } from '@/api/generated/model'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { ITEM_STATUS_ACTIVE_TONES, ITEM_STATUS_LABELS, ITEM_STATUSES } from '@/lib/statuses'

type Props = { value: ItemStatus; onChange: (status: ItemStatus) => void; id?: string }

/** One tap to set a status. */
export function ItemStatusToggle({ value, onChange, id }: Props) {
  return (
    <ToggleGroup
      id={id}
      type="single"
      variant="outline"
      value={value}
      // Radix sends "" when the active one is tapped again; a status is always required.
      onValueChange={(next) => next && onChange(next as ItemStatus)}
      className="flex-wrap"
    >
      {ITEM_STATUSES.map((status) => (
        <ToggleGroupItem key={status} value={status} className={ITEM_STATUS_ACTIVE_TONES[status]}>
          {ITEM_STATUS_LABELS[status]}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  )
}
