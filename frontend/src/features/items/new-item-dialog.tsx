import { useState, type FormEvent, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import { useCreateItem } from '@/api/generated/items/items'
import type { ItemStatus } from '@/api/generated/model'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { LocationTreeSelect } from '@/features/locations/location-tree-select'
import { ItemStatusToggle } from './item-status-toggle'

type Props = {
  trigger: ReactNode
  /** Creates a child of this item, starting in the same location, and stays on the page. */
  parent?: { id: number; locationId: number | null }
}

export function NewItemDialog({ trigger, parent }: Props) {
  const navigate = useNavigate()
  const createItem = useCreateItem()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [status, setStatus] = useState<ItemStatus>('have')
  const [locationId, setLocationId] = useState<number | null>(parent?.locationId ?? null)

  const onOpenChange = (next: boolean) => {
    setOpen(next)
    if (next) {
      setName('')
      setStatus('have')
      setLocationId(parent?.locationId ?? null)
    }
  }

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    const data = { name, status, location_id: locationId, parent_id: parent?.id ?? null }
    createItem.mutate(
      { data },
      {
        onSuccess: (item) => {
          setOpen(false)
          if (!parent) navigate(`/items/${item.id}`)
        },
      },
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <form onSubmit={submit} className="grid gap-5">
          <DialogHeader>
            <DialogTitle>{parent ? 'New child item' : 'New item'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-2">
            <Label htmlFor="new-item-name">Name</Label>
            <Input
              id="new-item-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="new-item-status">Status</Label>
            <ItemStatusToggle id="new-item-status" value={status} onChange={setStatus} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="new-item-location">Location</Label>
            <LocationTreeSelect
              id="new-item-location"
              value={locationId}
              onChange={setLocationId}
              noneLabel="No location"
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!name.trim() || createItem.isPending}>
              Create
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
