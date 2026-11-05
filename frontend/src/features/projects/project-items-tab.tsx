import { Package, X } from 'lucide-react'
import { useCreateItem, useListItems } from '@/api/generated/items/items'
import type { ProjectItemOut, Requirement } from '@/api/generated/model'
import {
  useLinkProjectItem,
  useListProjectItems,
  useUnlinkProjectItem,
} from '@/api/generated/projects/projects'
import { EditableText } from '@/components/editable-text'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { Button } from '@/components/ui/button'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { useLocationTree } from '@/features/locations/location-tree'
import { ItemRow } from '@/features/items/item-row'
import { REQUIREMENT_LABELS } from '@/lib/statuses'
import { LoadError } from '@/components/load-error'
import { ListSkeleton } from '@/components/loading'

function LinkedItem({ projectId, link }: { projectId: number; link: ProjectItemOut }) {
  const linkItem = useLinkProjectItem()
  const unlinkItem = useUnlinkProjectItem()
  const { byId: locations } = useLocationTree()
  const { item } = link
  const save = (changes: { requirement?: Requirement; note?: string }) =>
    linkItem.mutate({
      projectId,
      itemId: item.id,
      data: { requirement: link.requirement, note: link.note, ...changes },
    })

  return (
    <div className="py-1">
      <div className="flex items-center gap-1">
        <div className="min-w-0 flex-1">
          <ItemRow
            item={item}
            locationPath={
              item.location_id == null ? undefined : locations.get(item.location_id)?.path
            }
          />
        </div>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label={`Unlink ${item.name}`}
          onClick={() => unlinkItem.mutate({ projectId, itemId: item.id })}
        >
          <X />
        </Button>
      </div>
      <div className="flex flex-wrap items-center gap-2 pr-3 pl-3">
        <ToggleGroup
          type="single"
          variant="outline"
          size="sm"
          value={link.requirement}
          onValueChange={(next) => next && save({ requirement: next as Requirement })}
          aria-label={`How much ${item.name} is needed`}
        >
          {(Object.keys(REQUIREMENT_LABELS) as Requirement[]).map((requirement) => (
            <ToggleGroupItem key={requirement} value={requirement}>
              {REQUIREMENT_LABELS[requirement]}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        <EditableText
          value={link.note}
          onSave={(note) => save({ note })}
          allowEmpty
          aria-label={`Note for ${item.name}`}
          placeholder="Add a note, e.g. need 2"
          className="min-w-40 flex-1 text-sm"
        />
      </div>
    </div>
  )
}

export function ProjectItemsTab({ projectId }: { projectId: number }) {
  const { data: links, isPending, error, refetch } = useListProjectItems(projectId)
  const { data: allItems = [] } = useListItems()
  const createItem = useCreateItem()
  const linkItem = useLinkProjectItem()

  const linkedIds = new Set(links?.map((link) => link.item.id))
  const link = (itemId: number) =>
    linkItem.mutate({ projectId, itemId, data: { requirement: 'required', note: '' } })
  const groups = (['required', 'nice_to_have'] as Requirement[])
    .map((requirement) => ({
      requirement,
      links: links?.filter((link) => link.requirement === requirement) ?? [],
    }))
    .filter((group) => group.links.length > 0)

  return (
    <div className="grid gap-4">
      <EntityPicker
        options={allItems
          .filter((item) => !linkedIds.has(item.id))
          .map((item) => ({ id: item.id, label: item.name }))}
        value={undefined}
        onChange={(id) => id != null && link(id)}
        placeholder="Link an item"
        searchPlaceholder="Find or create an item…"
        // Something a project needs but isn't in Items yet is probably not on hand.
        onCreate={(name) =>
          createItem.mutate(
            { data: { name, status: 'need' } },
            { onSuccess: (item) => link(item.id) },
          )
        }
        className="w-full sm:w-80"
      />
      {isPending ? (
        <ListSkeleton rows={3} />
      ) : error ? (
        <LoadError what="linked items" error={error} onRetry={refetch} />
      ) : groups.length === 0 ? (
        <EmptyState
          icon={Package}
          title="No items linked yet"
          description="Link the tools and materials this project needs to see how ready it is."
        />
      ) : (
        groups.map((group) => (
          <section key={group.requirement}>
            <h2 className="mb-1 text-sm font-medium">{REQUIREMENT_LABELS[group.requirement]}</h2>
            <div className="-mx-3 divide-y">
              {group.links.map((link) => (
                <LinkedItem key={link.item.id} projectId={projectId} link={link} />
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  )
}
