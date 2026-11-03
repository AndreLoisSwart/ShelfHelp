import { useState, type FormEvent, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import type { ProjectStatus } from '@/api/generated/model'
import { useCreateProject } from '@/api/generated/projects/projects'
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
import { ProjectStatusToggle } from './project-status-toggle'

export function NewProjectDialog({ trigger }: { trigger: ReactNode }) {
  const navigate = useNavigate()
  const createProject = useCreateProject()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [status, setStatus] = useState<ProjectStatus>('someday')
  const [nextStep, setNextStep] = useState('')

  const onOpenChange = (next: boolean) => {
    setOpen(next)
    if (next) {
      setName('')
      setStatus('someday')
      setNextStep('')
    }
  }

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    createProject.mutate(
      { data: { name, status, next_step: nextStep } },
      {
        onSuccess: (project) => {
          setOpen(false)
          navigate(`/projects/${project.id}`)
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
            <DialogTitle>New project</DialogTitle>
          </DialogHeader>
          <div className="grid gap-2">
            <Label htmlFor="new-project-name">Name</Label>
            <Input
              id="new-project-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="new-project-status">Status</Label>
            <ProjectStatusToggle id="new-project-status" value={status} onChange={setStatus} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="new-project-next">Next step</Label>
            <Input
              id="new-project-next"
              value={nextStep}
              onChange={(e) => setNextStep(e.target.value)}
              maxLength={500}
              placeholder="Optional"
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!name.trim() || createProject.isPending}>
              Create
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
