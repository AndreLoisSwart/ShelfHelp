import { ChevronRight, ListTodo } from 'lucide-react'
import { useState } from 'react'
import { useCreateTask, useListTasks, useReorderTasks } from '@/api/generated/tasks/tasks'
import { EmptyState } from '@/components/empty-state'
import { InlineAddForm } from '@/components/inline-add-form'
import { LoadError } from '@/components/load-error'
import { ListSkeleton } from '@/components/loading'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { SortableTaskList } from './sortable-task-list'
import { TaskRow } from './task-row'

export function ProjectTasksTab({ projectId }: { projectId: number }) {
  const { data: tasks, isPending, error, refetch } = useListTasks({ project_id: projectId })
  const createTask = useCreateTask()
  const reorderTasks = useReorderTasks()
  const [showDone, setShowDone] = useState(false)

  const open = tasks?.filter((task) => task.done_at === null) ?? []
  const done = tasks?.filter((task) => task.done_at !== null) ?? []

  return (
    <div className="grid gap-4">
      <div className="sm:max-w-md">
        <InlineAddForm
          placeholder="Add a task"
          onAdd={(title) => createTask.mutateAsync({ data: { title, project_id: projectId } })}
        />
      </div>
      {isPending ? (
        <ListSkeleton rows={3} />
      ) : error ? (
        <LoadError what="tasks" error={error} onRetry={refetch} />
      ) : open.length === 0 && done.length === 0 ? (
        <EmptyState
          icon={ListTodo}
          title="No tasks yet"
          description="Break the project into steps. The first open one is its next step."
        />
      ) : (
        <>
          {open.length > 0 ? (
            <SortableTaskList
              tasks={open}
              onReorder={(task_ids) =>
                reorderTasks.mutate({ data: { project_id: projectId, task_ids } })
              }
            />
          ) : (
            <p className="text-sm text-muted-foreground">
              All done. Add the next task when there is one.
            </p>
          )}
          {done.length > 0 && (
            <section>
              <Button
                variant="ghost"
                size="sm"
                className="-ml-2 text-muted-foreground"
                aria-expanded={showDone}
                onClick={() => setShowDone((shown) => !shown)}
              >
                <ChevronRight className={cn('transition-transform', showDone && 'rotate-90')} />
                {done.length} done
              </Button>
              {showDone && (
                <div className="-mx-3 mt-1">
                  {done.map((task) => (
                    <TaskRow key={task.id} task={task} />
                  ))}
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  )
}
