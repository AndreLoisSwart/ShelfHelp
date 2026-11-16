import { ListTodo, Trash2, X } from 'lucide-react'
import type { ReactNode } from 'react'
import { useNavigate, useParams } from 'react-router'
import { errorMessage } from '@/api/fetcher'
import { useCreateItem, useListItems } from '@/api/generated/items/items'
import type { TaskUpdate } from '@/api/generated/model'
import { useListProjects } from '@/api/generated/projects/projects'
import { useDeleteTask, useGetTask, useUpdateTask } from '@/api/generated/tasks/tasks'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { EditableText } from '@/components/editable-text'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { DetailSkeleton } from '@/components/loading'
import { NotFound } from '@/components/not-found'
import { Button } from '@/components/ui/button'
import { InboxNotice } from '@/features/inbox/inbox-notice'
import { ItemRow } from '@/features/items/item-row'
import { useLocationTree } from '@/features/locations/location-tree'
import { TagEditor } from '@/features/tags/tag-editor'
import { formatDate } from '@/lib/format'
import { TaskCheckbox } from './task-checkbox'
import { itemReadiness } from './readiness'
import { useToggleTask } from './use-toggle-task'

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

export function TaskDetailPage() {
  const taskId = Number(useParams().id)
  const navigate = useNavigate()
  const { data: task, error, isPending } = useGetTask(taskId)
  const { data: projects = [] } = useListProjects()
  const { data: allItems = [] } = useListItems()
  const { byId: locations } = useLocationTree()
  const updateTask = useUpdateTask()
  const deleteTask = useDeleteTask()
  const createItem = useCreateItem()
  const toggle = useToggleTask()

  if (isPending) return <DetailSkeleton />
  if (error) {
    if (error.status === 404 || error.status === 422) return <NotFound />
    return (
      <EmptyState
        icon={ListTodo}
        title="Couldn't load this task"
        description={errorMessage(error)}
      />
    )
  }

  const save = (data: TaskUpdate) => updateTask.mutate({ taskId, data })
  const done = task.done_at !== null
  const itemIds = task.items.map((item) => item.id)
  const linkItem = (id: number) => save({ item_ids: [...itemIds, id] })
  const readiness = itemReadiness(task.readiness)

  return (
    <>
      <div className="mb-1 flex items-start gap-3">
        <TaskCheckbox
          done={done}
          onToggle={() => toggle(task)}
          aria-label={done ? 'Reopen' : 'Tick off'}
          className="mt-3 size-6"
        />
        <EditableText
          value={task.title}
          onSave={(title) => save({ title })}
          aria-label="Title"
          className={
            done
              ? '-ml-2 text-2xl font-semibold tracking-tight text-muted-foreground line-through'
              : '-ml-2 text-2xl font-semibold tracking-tight'
          }
        />
        <ConfirmDialog
          title={`Delete ${task.title}?`}
          description="Linked items are kept. This can't be undone."
          onConfirm={() =>
            deleteTask.mutate(
              { taskId },
              {
                onSuccess: () =>
                  navigate(task.project ? `/projects/${task.project.id}?tab=tasks` : '/tasks', {
                    replace: true,
                  }),
              },
            )
          }
          trigger={
            <Button variant="ghost" size="icon" className="mt-1" aria-label="Delete task">
              <Trash2 />
            </Button>
          }
        />
      </div>
      <p className="mb-6 text-xs text-muted-foreground">
        Added {formatDate(task.created_at)}
        {task.done_at && ` · Done ${formatDate(task.done_at)}`}
      </p>

      {task.in_inbox && <InboxNotice onDone={() => save({ in_inbox: false })} className="mb-6" />}
      <dl className="grid gap-x-6 gap-y-4 sm:grid-cols-[7rem_1fr]">
        <Field label="Project" htmlFor="task-project">
          <EntityPicker
            id="task-project"
            options={projects.map((p) => ({ id: p.id, label: p.name }))}
            value={task.project?.id ?? null}
            onChange={(project_id) => save({ project_id })}
            placeholder="No project"
            noneLabel="No project"
            searchPlaceholder="Find a project…"
            className="w-full sm:w-80"
          />
        </Field>
        <Field label="Tags">
          <TagEditor value={task.tags} onChange={(tag_ids) => save({ tag_ids })} />
        </Field>
      </dl>

      <section className="mt-8">
        <h2 className="mb-2 text-sm font-medium">Description</h2>
        <EditableText
          multiline
          value={task.description}
          onSave={(description) => save({ description })}
          aria-label="Description"
          placeholder="Details, measurements, how to do it…"
          className="-ml-2 resize-y text-sm"
        />
      </section>

      <section className="mt-8">
        <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-sm font-medium">Items</h2>
          {readiness && <span className="text-xs text-muted-foreground">{readiness}</span>}
        </div>
        <EntityPicker
          options={allItems
            .filter((item) => !itemIds.includes(item.id))
            .map((item) => ({ id: item.id, label: item.name }))}
          value={undefined}
          onChange={(id) => id != null && linkItem(id)}
          placeholder="Link an item"
          searchPlaceholder="Find or create an item…"
          // Something a task needs but isn't in Items yet is probably not on hand.
          onCreate={(name) =>
            createItem.mutate(
              { data: { name, status: 'need' } },
              { onSuccess: (item) => linkItem(item.id) },
            )
          }
          className="mb-2 w-full sm:w-80"
        />
        {task.items.length > 0 ? (
          <div className="-mx-3 divide-y">
            {task.items.map((item) => (
              <div key={item.id} className="flex items-center gap-1">
                <div className="min-w-0 flex-1">
                  <ItemRow
                    item={item}
                    locationPath={
                      item.location_id == null ? undefined : locations.get(item.location_id)?.path
                    }
                  />
                </div>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  aria-label={`Unlink ${item.name}`}
                  onClick={() => save({ item_ids: itemIds.filter((id) => id !== item.id) })}
                >
                  <X />
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">The tools and materials this task needs.</p>
        )}
      </section>

      <p className="mt-10 text-xs text-muted-foreground">Updated {formatDate(task.updated_at)}</p>
    </>
  )
}
