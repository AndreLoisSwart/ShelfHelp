import { Package, Plus, X } from 'lucide-react'
import { useSearchParams } from 'react-router'
import { useListItems } from '@/api/generated/items/items'
import type { ItemStatus } from '@/api/generated/model'
import { useListTags } from '@/api/generated/tags/tags'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { FilterBar } from '@/components/filter-bar'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { useLocationTree } from '@/features/locations/location-tree'
import { LocationTreeSelect } from '@/features/locations/location-tree-select'
import { STATUS_ACTIVE_TONES, ITEM_STATUS_LABELS, ITEM_STATUSES } from '@/lib/statuses'
import { ItemRow } from './item-row'
import { nestItems } from './item-tree'
import { NewItemDialog } from './new-item-dialog'

const newItemButton = (
  <Button>
    <Plus />
    New item
  </Button>
)

export function ItemsPage() {
  // Filters live in the URL, so they survive going back from an item.
  const [params, setParams] = useSearchParams()
  const locationId = params.has('location') ? Number(params.get('location')) : undefined
  const statuses = params.getAll('status') as ItemStatus[]
  const tagId = params.has('tag') ? Number(params.get('tag')) : undefined
  const filtered = locationId !== undefined || statuses.length > 0 || tagId !== undefined

  const setFilter = (key: string, values: (string | number)[]) => {
    const next = new URLSearchParams(params)
    next.delete(key)
    values.forEach((value) => next.append(key, String(value)))
    setParams(next, { replace: true })
  }

  const { data: items, isPending } = useListItems({
    location_id: locationId,
    status: statuses.length ? statuses : undefined,
    tag_id: tagId !== undefined ? [tagId] : undefined,
  })
  const { data: tags = [] } = useListTags()
  const { byId: locations } = useLocationTree()

  return (
    <>
      <PageHeader title="Items" actions={<NewItemDialog trigger={newItemButton} />} />

      <FilterBar>
        <LocationTreeSelect
          value={locationId ?? null}
          onChange={(id) => setFilter('location', id === null ? [] : [id])}
          noneLabel="All locations"
          className="w-full sm:w-56"
        />
        <EntityPicker
          options={tags.map((tag) => ({ id: tag.id, label: tag.name }))}
          value={tagId ?? null}
          onChange={(id) => setFilter('tag', id === null ? [] : [id])}
          placeholder="All tags"
          noneLabel="All tags"
          searchPlaceholder="Find a tag…"
          className="w-full sm:w-40"
        />
        <ToggleGroup
          type="multiple"
          variant="outline"
          size="sm"
          value={statuses}
          onValueChange={(next) => setFilter('status', next)}
          className="flex-wrap"
          aria-label="Status"
        >
          {ITEM_STATUSES.map((status) => (
            <ToggleGroupItem key={status} value={status} className={STATUS_ACTIVE_TONES[status]}>
              {ITEM_STATUS_LABELS[status]}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        {filtered && (
          <Button variant="ghost" size="sm" onClick={() => setParams({}, { replace: true })}>
            <X />
            Clear
          </Button>
        )}
      </FilterBar>

      {isPending ? null : items?.length ? (
        <div className="-mx-3 divide-y">
          {nestItems(items).map(({ item, depth }) => (
            <ItemRow
              key={item.id}
              item={item}
              depth={depth}
              locationPath={
                item.location_id == null ? undefined : locations.get(item.location_id)?.path
              }
            />
          ))}
        </div>
      ) : filtered ? (
        <EmptyState icon={Package} title="No items match these filters" />
      ) : (
        <EmptyState
          icon={Package}
          title="No items yet"
          description="Tools, components, consumables and household goods."
        >
          <NewItemDialog trigger={newItemButton} />
        </EmptyState>
      )}
    </>
  )
}
