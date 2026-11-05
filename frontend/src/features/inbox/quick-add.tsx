import { FolderKanban, NotebookPen, Package } from 'lucide-react'
import { useState, type FormEvent, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import { toast } from 'sonner'
import { useCreateItem } from '@/api/generated/items/items'
import type { ItemStatus } from '@/api/generated/model'
import { useCreateNote } from '@/api/generated/notes/notes'
import { useCreateProject } from '@/api/generated/projects/projects'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { ITEM_STATUS_LABELS, STATUS_ACTIVE_TONES } from '@/lib/statuses'
import { useBackToClose } from '@/lib/use-back-to-close'
import { usePersistentState } from '@/lib/use-persistent-state'
import { QuickAddContext } from './use-quick-add'

const KINDS = ['item', 'note', 'project'] as const
type Kind = (typeof KINDS)[number]

const KIND_OPTIONS: Record<Kind, { label: string; icon: typeof Package; field: string }> = {
  item: { label: 'Item', icon: Package, field: 'Name' },
  note: { label: 'Note', icon: NotebookPen, field: 'Title' },
  project: { label: 'Project', icon: FolderKanban, field: 'Name' },
}

// Quick captures are either things you have or things to get; the rest is for sorting.
const QUICK_ITEM_STATUSES: ItemStatus[] = ['have', 'need']

export function QuickAddProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <QuickAddContext.Provider value={() => setOpen(true)}>
      {children}
      <QuickAddSheet open={open} onOpenChange={setOpen} />
    </QuickAddContext.Provider>
  )
}

type Props = { open: boolean; onOpenChange: (open: boolean) => void }

/** Type and name, saved to the inbox. A dialog on desktop, a bottom sheet on phones. */
export function QuickAddSheet({ open, onOpenChange }: Props) {
  const navigate = useNavigate()
  const createItem = useCreateItem()
  const createNote = useCreateNote()
  const createProject = useCreateProject()
  const [kind, setKind] = usePersistentState<Kind>('quick-add-kind', 'item', KINDS)
  const [name, setName] = useState('')
  const [status, setStatus] = useState<ItemStatus>('have')
  const pending = createItem.isPending || createNote.isPending || createProject.isPending
  useBackToClose(open, () => onOpenChange(false))

  const changeOpen = (next: boolean) => {
    onOpenChange(next)
    if (next) {
      setName('')
      setStatus('have')
    }
  }

  const added = (path: string) => {
    onOpenChange(false)
    // Opened from outside (not through changeOpen), so clear it for next time here.
    setName('')
    setStatus('have')
    toast.success('Added to the inbox', {
      action: { label: 'Open', onClick: () => navigate(path) },
    })
  }

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!name.trim() || pending) return
    if (kind === 'item') {
      createItem.mutate(
        { data: { name, status, in_inbox: true } },
        { onSuccess: (item) => added(`/items/${item.id}`) },
      )
    } else if (kind === 'note') {
      createNote.mutate(
        { data: { title: name, in_inbox: true } },
        { onSuccess: (note) => added(`/notes/${note.id}`) },
      )
    } else {
      createProject.mutate(
        { data: { name, in_inbox: true } },
        { onSuccess: (project) => added(`/projects/${project.id}`) },
      )
    }
  }

  return (
    <Dialog open={open} onOpenChange={changeOpen}>
      <DialogContent className="max-md:top-auto max-md:bottom-0 max-md:max-w-full max-md:translate-y-0 max-md:rounded-b-none max-md:pb-[calc(1rem+env(safe-area-inset-bottom))] max-md:data-open:slide-in-from-bottom-10 max-md:data-open:zoom-in-100 sm:max-w-md">
        <form onSubmit={submit} className="grid gap-5">
          <DialogHeader>
            <DialogTitle>Quick add</DialogTitle>
            <DialogDescription>Saved to the inbox, to sort later.</DialogDescription>
          </DialogHeader>
          <ToggleGroup
            type="single"
            variant="outline"
            value={kind}
            onValueChange={(next) => next && setKind(next as Kind)}
            aria-label="Type"
            className="w-full"
          >
            {KINDS.map((k) => {
              const { label, icon: Icon } = KIND_OPTIONS[k]
              return (
                <ToggleGroupItem key={k} value={k} className="flex-1">
                  <Icon />
                  {label}
                </ToggleGroupItem>
              )
            })}
          </ToggleGroup>
          <div className="grid gap-2">
            <Label htmlFor="quick-add-name">{KIND_OPTIONS[kind].field}</Label>
            <Input
              id="quick-add-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={200}
              autoComplete="off"
              autoFocus
            />
          </div>
          {kind === 'item' && (
            <ToggleGroup
              type="single"
              variant="outline"
              value={status}
              onValueChange={(next) => next && setStatus(next as ItemStatus)}
              aria-label="Status"
              className="justify-start"
            >
              {QUICK_ITEM_STATUSES.map((s) => (
                <ToggleGroupItem key={s} value={s} className={STATUS_ACTIVE_TONES[s]}>
                  {ITEM_STATUS_LABELS[s]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          )}
          <DialogFooter>
            <Button type="submit" disabled={!name.trim() || pending}>
              Add to inbox
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
