import { toast } from 'sonner'
import { useUpdateTask } from '@/api/generated/tasks/tasks'

type Toggleable = { id: number; title: string; done_at?: string | null }

/** Ticks a task off (with Undo) or reopens it. */
export function useToggleTask() {
  const updateTask = useUpdateTask()
  return (task: Toggleable) => {
    const done = !task.done_at
    updateTask.mutate(
      { taskId: task.id, data: { done } },
      {
        onSuccess: () => {
          if (!done) return
          toast.success(`Done: ${task.title}`, {
            action: {
              label: 'Undo',
              onClick: () => updateTask.mutate({ taskId: task.id, data: { done: false } }),
            },
          })
        },
      },
    )
  }
}
