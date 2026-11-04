import { useState, type FormEvent, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import { useCreateNote } from '@/api/generated/notes/notes'
import { useListProjects } from '@/api/generated/projects/projects'
import { EntityPicker } from '@/components/entity-picker'
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

type Props = {
  trigger: ReactNode
  /** Starts the note in this project. */
  projectId?: number
}

export function NewNoteDialog({ trigger, projectId }: Props) {
  const navigate = useNavigate()
  const createNote = useCreateNote()
  const { data: projects = [] } = useListProjects()
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [project, setProject] = useState<number | null>(projectId ?? null)

  const onOpenChange = (next: boolean) => {
    setOpen(next)
    if (next) {
      setTitle('')
      setProject(projectId ?? null)
    }
  }

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    createNote.mutate(
      { data: { title, project_id: project } },
      {
        onSuccess: (note) => {
          setOpen(false)
          navigate(`/notes/${note.id}`)
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
            <DialogTitle>New note</DialogTitle>
          </DialogHeader>
          <div className="grid gap-2">
            <Label htmlFor="new-note-title">Title</Label>
            <Input
              id="new-note-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="new-note-project">Project</Label>
            <EntityPicker
              id="new-note-project"
              options={projects.map((p) => ({ id: p.id, label: p.name }))}
              value={project}
              onChange={setProject}
              placeholder="No project"
              noneLabel="No project"
              searchPlaceholder="Find a project…"
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!title.trim() || createNote.isPending}>
              Create
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
