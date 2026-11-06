import { CornerDownRight, Ellipsis, FolderInput, Tags, Trash2 } from 'lucide-react'
import { useState } from 'react'
import {
  useCreateLocation,
  useDeleteLocation,
  useUpdateLocation,
} from '@/api/generated/locations/locations'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { EditableText } from '@/components/editable-text'
import { InlineAddForm } from '@/components/inline-add-form'
import { TagChips } from '@/components/tag-chips'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { plural } from '@/lib/format'
import { subtreeIds, useLocationTree, type LocationNode } from './location-tree'
import { LocationTagEditor } from './location-tag-editor'
import { LocationTreeSelect } from './location-tree-select'

const INDENT = 20

function LocationRow({ node }: { node: LocationNode }) {
  const createLocation = useCreateLocation()
  const updateLocation = useUpdateLocation()
  const deleteLocation = useDeleteLocation()
  const [adding, setAdding] = useState(false)
  const [moving, setMoving] = useState(false)
  const [editingTags, setEditingTags] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const inUse = node.children.length > 0 || node.item_count > 0

  return (
    <li>
      <div
        className="flex items-center gap-2 rounded-md py-1 pr-1 hover:bg-muted/60"
        style={{ paddingLeft: node.depth * INDENT }}
      >
        <EditableText
          value={node.name}
          onSave={(name) => updateLocation.mutate({ locationId: node.id, data: { name } })}
          aria-label={`Name of ${node.path}`}
          className={node.depth === 0 ? 'font-medium' : undefined}
        />
        {!editingTags && <TagChips tags={node.tags} className="max-w-1/2 shrink-0 justify-end" />}
        {node.item_count > 0 && (
          <span className="shrink-0 text-xs text-muted-foreground">
            {plural(node.item_count, 'item')}
          </span>
        )}
        {/* Not modal, so the dialogs it opens get focus and clicks back properly. */}
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon-sm" aria-label={`Actions for ${node.path}`}>
              <Ellipsis />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onSelect={() => setAdding(true)}>
              <CornerDownRight />
              Add sub-location
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setEditingTags((open) => !open)}>
              <Tags />
              {editingTags ? 'Done with tags' : 'Tags…'}
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setMoving(true)}>
              <FolderInput />
              Move…
            </DropdownMenuItem>
            <DropdownMenuItem
              variant="destructive"
              disabled={inUse}
              onSelect={() => setDeleting(true)}
            >
              <Trash2 />
              {inUse ? 'Delete (not empty)' : 'Delete'}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {editingTags && (
        <div
          className="flex flex-wrap items-center gap-2 pt-1 pb-2"
          style={{ paddingLeft: node.depth * INDENT + 8 }}
        >
          <span className="text-xs text-muted-foreground">Given to items put here:</span>
          <LocationTagEditor node={node} />
          <Button variant="ghost" size="sm" onClick={() => setEditingTags(false)}>
            Done
          </Button>
        </div>
      )}

      {adding && (
        <div className="py-1" style={{ paddingLeft: (node.depth + 1) * INDENT }}>
          <InlineAddForm
            placeholder={`New location inside ${node.name}`}
            autoFocus
            onCancel={() => setAdding(false)}
            onAdd={(name) =>
              createLocation
                .mutateAsync({ data: { name, parent_id: node.id } })
                .then(() => setAdding(false))
            }
          />
        </div>
      )}

      {node.children.length > 0 && (
        <ul>
          {node.children.map((child) => (
            <LocationRow key={child.id} node={child} />
          ))}
        </ul>
      )}

      <Dialog open={moving} onOpenChange={setMoving}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Move {node.name}</DialogTitle>
            <DialogDescription>Its sub-locations and items move with it.</DialogDescription>
          </DialogHeader>
          <LocationTreeSelect
            value={node.parent_id}
            exclude={subtreeIds(node)}
            noneLabel="Top level (a zone)"
            onChange={(parentId) =>
              updateLocation.mutate(
                { locationId: node.id, data: { parent_id: parentId } },
                { onSuccess: () => setMoving(false) },
              )
            }
          />
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleting}
        onOpenChange={setDeleting}
        title={`Delete ${node.name}?`}
        onConfirm={() => deleteLocation.mutate({ locationId: node.id })}
      />
    </li>
  )
}

export function LocationTreeEditor() {
  const { roots, isPending } = useLocationTree()
  const createLocation = useCreateLocation()

  return (
    <section>
      <h2 className="text-lg font-semibold">Locations</h2>
      <p className="mt-1 mb-4 text-sm text-muted-foreground">
        Top-level locations are zones, like Home and Workshop. Each zone gets its own shopping list.
        Tags on a location are given to items put there. Click a name to rename it.
      </p>
      {roots.length > 0 ? (
        <ul className="mb-4">
          {roots.map((node) => (
            <LocationRow key={node.id} node={node} />
          ))}
        </ul>
      ) : (
        !isPending && <p className="mb-4 text-sm text-muted-foreground">No locations yet.</p>
      )}
      <InlineAddForm
        placeholder="New zone, e.g. Workshop"
        onAdd={(name) => createLocation.mutateAsync({ data: { name } })}
      />
    </section>
  )
}
