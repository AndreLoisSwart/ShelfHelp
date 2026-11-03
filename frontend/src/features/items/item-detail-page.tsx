import { Package, Plus, Trash2 } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { errorMessage } from '@/api/fetcher'
import { useDeleteItem, useGetItem, useListItems, useUpdateItem } from '@/api/generated/items/items'
import type { ItemUpdate } from '@/api/generated/model'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { EditableText } from '@/components/editable-text'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { NotFound } from '@/components/not-found'
import { StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { useLocationTree } from '@/features/locations/location-tree'
import { LocationTreeSelect } from '@/features/locations/location-tree-select'
import { TagEditor } from '@/features/tags/tag-editor'
import { formatDate } from '@/lib/format'
import { REQUIREMENT_LABELS } from '@/lib/statuses'
import { ItemRow } from './item-row'
import { ItemStatusToggle } from './item-status-toggle'
import { subtreeIds } from './item-tree'
import { NewItemDialog } from './new-item-dialog'

function Field({
  label,
  htmlFor,
  children,
}: {
  label: string
  htmlFor?: string
  children: ReactNode
}) {
  return (
    <>
      <dt className="pt-1.5 text-sm text-muted-foreground">
        <label htmlFor={htmlFor}>{label}</label>
      </dt>
      <dd className="min-w-0">{children}</dd>
    </>
  )
}

export function ItemDetailPage() {
  const itemId = Number(useParams().id)
  const navigate = useNavigate()
  const { data: item, error, isPending } = useGetItem(itemId)
  const { data: allItems = [] } = useListItems()
  const { byId: locations } = useLocationTree()
  const updateItem = useUpdateItem()
  const deleteItem = useDeleteItem()

  if (isPending) return null
  if (error) {
    if (error.status === 404 || error.status === 422) return <NotFound />
    return (
      <EmptyState
        icon={Package}
        title="Couldn't load this item"
        description={errorMessage(error)}
      />
    )
  }

  const save = (data: ItemUpdate) => updateItem.mutate({ itemId, data })
  const notParent = subtreeIds(allItems, itemId)
  const parentOptions = allItems
    .filter((other) => !notParent.has(other.id))
    .map((other) => ({ id: other.id, label: other.name }))

  return (
    <>
      <div className="mb-6 flex items-start gap-2">
        <EditableText
          value={item.name}
          onSave={(name) => save({ name })}
          aria-label="Name"
          className="-ml-2 text-2xl font-semibold tracking-tight"
        />
        <ConfirmDialog
          title={`Delete ${item.name}?`}
          description={
            item.children.length > 0
              ? 'Its child items will become top-level items.'
              : "This can't be undone."
          }
          onConfirm={() =>
            deleteItem.mutate(
              { itemId },
              { onSuccess: () => navigate('/items', { replace: true }) },
            )
          }
          trigger={
            <Button variant="ghost" size="icon" className="mt-1" aria-label="Delete item">
              <Trash2 />
            </Button>
          }
        />
      </div>

      <dl className="grid gap-x-6 gap-y-4 sm:grid-cols-[7rem_1fr]">
        <Field label="Status" htmlFor="item-status">
          <ItemStatusToggle
            id="item-status"
            value={item.status}
            onChange={(status) => save({ status })}
          />
        </Field>
        <Field label="Location" htmlFor="item-location">
          <LocationTreeSelect
            id="item-location"
            value={item.location_id}
            onChange={(location_id) => save({ location_id })}
            noneLabel="No location"
            className="w-full sm:w-80"
          />
        </Field>
        <Field label="Part of" htmlFor="item-parent">
          <EntityPicker
            id="item-parent"
            options={parentOptions}
            value={item.parent_id}
            onChange={(parent_id) => save({ parent_id })}
            placeholder="No parent item"
            noneLabel="No parent item"
            searchPlaceholder="Find an item…"
            className="w-full sm:w-80"
          />
        </Field>
        <Field label="Tags">
          <TagEditor value={item.tags} onChange={(tag_ids) => save({ tag_ids })} />
        </Field>
      </dl>

      <section className="mt-8">
        <h2 className="mb-2 text-sm font-medium">Description</h2>
        <EditableText
          multiline
          value={item.description}
          onSave={(description) => save({ description })}
          aria-label="Description"
          placeholder="Model, size, where it came from…"
          className="-ml-2 resize-y text-sm"
        />
      </section>

      <section className="mt-8">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-medium">Parts and accessories</h2>
          <NewItemDialog
            parent={{ id: item.id, locationId: item.location_id }}
            trigger={
              <Button variant="outline" size="sm">
                <Plus />
                Add
              </Button>
            }
          />
        </div>
        {item.children.length > 0 ? (
          <div className="-mx-3 divide-y">
            {item.children.map((child) => (
              <ItemRow
                key={child.id}
                item={child}
                locationPath={
                  child.location_id == null ? undefined : locations.get(child.location_id)?.path
                }
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">None yet, e.g. blades for a saw.</p>
        )}
      </section>

      <section className="mt-8">
        <h2 className="mb-2 text-sm font-medium">Used in</h2>
        {item.projects.length > 0 ? (
          <div className="-mx-3 divide-y">
            {item.projects.map(({ project, requirement, note }) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}?tab=items`}
                className="flex items-center gap-3 rounded-md px-3 py-2.5 hover:bg-muted/60"
              >
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium">{project.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {REQUIREMENT_LABELS[requirement]}
                    {note && ` · ${note}`}
                  </div>
                </div>
                <StatusBadge status={project.status} />
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Not linked to any projects. Link it from a project's Items tab.
          </p>
        )}
      </section>

      <p className="mt-10 text-xs text-muted-foreground">
        Added {formatDate(item.created_at)} · Updated {formatDate(item.updated_at)}
      </p>
    </>
  )
}
