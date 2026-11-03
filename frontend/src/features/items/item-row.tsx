import { CornerDownRight } from 'lucide-react'
import { Link } from 'react-router'
import type { ItemSummary } from '@/api/generated/model'
import { StatusBadge } from '@/components/status-badge'
import { TagChips } from '@/components/tag-chips'

type Props = { item: ItemSummary; depth?: number; locationPath?: string }

export function ItemRow({ item, depth = 0, locationPath }: Props) {
  return (
    <Link
      to={`/items/${item.id}`}
      className="flex items-center gap-3 rounded-md py-2.5 pr-3 hover:bg-muted/60"
      style={{ paddingLeft: 12 + depth * 20 }}
    >
      {depth > 0 && <CornerDownRight className="size-3.5 shrink-0 text-muted-foreground" />}
      <div className="min-w-0 flex-1">
        <div className="truncate font-medium">{item.name}</div>
        {(locationPath || item.tags.length > 0) && (
          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
            {locationPath && <span className="truncate">{locationPath}</span>}
            <TagChips tags={item.tags} />
          </div>
        )}
      </div>
      <StatusBadge status={item.status} />
    </Link>
  )
}
