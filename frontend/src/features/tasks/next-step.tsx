import { Link } from 'react-router'
import type { NextTask } from '@/api/generated/model'
import { useCreateTask } from '@/api/generated/tasks/tasks'
import { EditableText } from '@/components/editable-text'
import { cn } from '@/lib/utils'
import { TaskCheckbox } from './task-checkbox'
import { useToggleTask } from './use-toggle-task'

type Props = {
  projectId: number
  projectName: string
  nextTask: NextTask | null
  className?: string
}

/** A project's next step: its first open task, ticked off right here. Without one,
 * a field to add it. */
export function NextStep({ projectId, projectName, nextTask, className }: Props) {
  const createTask = useCreateTask()
  const toggle = useToggleTask()

  if (!nextTask) {
    return (
      <EditableText
        value=""
        onSave={(title) => createTask.mutate({ data: { title, project_id: projectId } })}
        aria-label={`Add a next step for ${projectName}`}
        placeholder="Add a next step"
        className={cn('-my-1', className)}
      />
    )
  }
  return (
    <div className={cn('flex min-w-0 items-start gap-2', className)}>
      <TaskCheckbox
        done={false}
        onToggle={() => toggle({ ...nextTask, done_at: null })}
        aria-label={`Tick off ${nextTask.title}`}
        className="mt-0.5"
      />
      <Link to={`/tasks/${nextTask.id}`} className="min-w-0 wrap-anywhere hover:underline">
        {nextTask.title}
      </Link>
    </div>
  )
}
