import type { ProjectStatus } from '@/api/generated/model'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { PROJECT_STATUS_LABELS, PROJECT_STATUSES, STATUS_ACTIVE_TONES } from '@/lib/statuses'

type Props = { value: ProjectStatus; onChange: (status: ProjectStatus) => void; id?: string }

export function ProjectStatusToggle({ value, onChange, id }: Props) {
  return (
    <ToggleGroup
      id={id}
      type="single"
      variant="outline"
      value={value}
      // Radix sends "" when the active one is tapped again; a status is always required.
      onValueChange={(next) => next && onChange(next as ProjectStatus)}
      className="flex-wrap"
    >
      {PROJECT_STATUSES.map((status) => (
        <ToggleGroupItem key={status} value={status} className={STATUS_ACTIVE_TONES[status]}>
          {PROJECT_STATUS_LABELS[status]}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  )
}
