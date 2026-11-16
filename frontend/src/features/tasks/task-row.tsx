import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { TaskSummary } from '@/api/generated/model'
import { TagChips } from '@/components/tag-chips'
import { cn } from '@/lib/utils'
import { itemReadiness } from './readiness'
import { TaskCheckbox } from './task-checkbox'
import { useToggleTask } from './use-toggle-task'

type Props = {
  task: TaskSummary
  /** Off where every task belongs to the same project. */
  showProject?: boolean
  /** Before the tick box, e.g. a drag handle. */
  handle?: ReactNode
  /** Before the details, e.g. a "Next step" label. */
  badge?: ReactNode
  /** At the end of the row. */
  actions?: ReactNode
  className?: string
}

export function TaskRow({ task, showProject, handle, badge, actions, className }: Props) {
  const toggle = useToggleTask()
  const done = task.done_at !== null
  const readiness = itemReadiness(task.readiness)
  const meta = badge || readiness || task.tags.length > 0 || (showProject && task.project)
  return (
    <div
      className={cn('flex items-start gap-3 rounded-md px-3 py-2.5 hover:bg-muted/60', className)}
    >
      {handle}
      <TaskCheckbox
        done={done}
        onToggle={() => toggle(task)}
        aria-label={done ? `Reopen ${task.title}` : `Tick off ${task.title}`}
        className="mt-0.5"
      />
      <div className="min-w-0 flex-1">
        <Link
          to={`/tasks/${task.id}`}
          className={cn(
            'block wrap-anywhere hover:underline',
            done && 'text-muted-foreground line-through',
          )}
        >
          {task.title}
        </Link>
        {meta && (
          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
            {badge}
            {showProject && task.project && <span>{task.project.name}</span>}
            {readiness && (
              <span
                className={cn(task.readiness.ready === task.readiness.total && 'text-status-green')}
              >
                {readiness}
              </span>
            )}
            <TagChips tags={task.tags} />
          </div>
        )}
      </div>
      {actions}
    </div>
  )
}
