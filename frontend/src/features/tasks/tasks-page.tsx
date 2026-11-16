import { ListTodo } from 'lucide-react'
import { Link, useSearchParams } from 'react-router'
import type { TaskSummary } from '@/api/generated/model'
import { useListProjects } from '@/api/generated/projects/projects'
import { useListTags } from '@/api/generated/tags/tags'
import { useCreateTask, useListTasks } from '@/api/generated/tasks/tasks'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { FilterBar } from '@/components/filter-bar'
import { InlineAddForm } from '@/components/inline-add-form'
import { LoadError } from '@/components/load-error'
import { ListSkeleton } from '@/components/loading'
import { PageHeader } from '@/components/page-header'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { TaskRow } from './task-row'

// A pseudo-project in the filter, for standalone tasks.
const NO_PROJECT = 0

type Group = { project: TaskSummary['project']; tasks: TaskSummary[] }

/** Standalone tasks first, then by project name. Tasks keep the server's order. */
function groupByProject(tasks: TaskSummary[]): Group[] {
  const groups = new Map<number, Group>()
  for (const task of tasks) {
    const key = task.project?.id ?? NO_PROJECT
    if (!groups.has(key)) groups.set(key, { project: task.project, tasks: [] })
    groups.get(key)!.tasks.push(task)
  }
  return [...groups.values()].sort((a, b) =>
    !a.project ? -1 : !b.project ? 1 : a.project.name.localeCompare(b.project.name),
  )
}

export function TasksPage() {
  const [params, setParams] = useSearchParams()
  const { data: projects = [] } = useListProjects()
  const { data: tags = [] } = useListTags()
  const createTask = useCreateTask()

  const projectFilter = params.has('project') ? Number(params.get('project')) : null
  const tagId = params.has('tag') ? Number(params.get('tag')) : null
  const showDone = params.get('done') === '1'
  const setFilter = (name: string, value: string | null) => {
    const next = new URLSearchParams(params)
    if (value === null) next.delete(name)
    else next.set(name, value)
    setParams(next, { replace: true })
  }

  const {
    data: tasks,
    isPending,
    error,
    refetch,
  } = useListTasks({
    project_id: projectFilter !== null && projectFilter !== NO_PROJECT ? projectFilter : undefined,
    no_project: projectFilter === NO_PROJECT || undefined,
    tag_id: tagId !== null ? [tagId] : undefined,
    done: showDone ? undefined : false,
  })
  const filtered = projectFilter !== null || tagId !== null
  // New tasks go to the project being looked at, otherwise they stand alone.
  const addTo = projectFilter !== null && projectFilter !== NO_PROJECT ? projectFilter : null
  const addToName = projects.find((p) => p.id === addTo)?.name

  return (
    <>
      <PageHeader title="Tasks" />
      <FilterBar>
        <EntityPicker
          options={[
            { id: NO_PROJECT, label: 'No project' },
            ...projects.map((p) => ({ id: p.id, label: p.name })),
          ]}
          value={projectFilter}
          onChange={(id) => setFilter('project', id === null ? null : String(id))}
          placeholder="All projects"
          noneLabel="All projects"
          searchPlaceholder="Find a project…"
          className="w-full sm:w-56"
        />
        <EntityPicker
          options={tags.map((tag) => ({ id: tag.id, label: tag.name }))}
          value={tagId}
          onChange={(id) => setFilter('tag', id === null ? null : String(id))}
          placeholder="All tags"
          noneLabel="All tags"
          searchPlaceholder="Find a tag…"
          className="w-40"
        />
        <div className="flex items-center gap-2">
          <Switch
            id="show-done"
            checked={showDone}
            onCheckedChange={(checked) => setFilter('done', checked ? '1' : null)}
          />
          <Label htmlFor="show-done" className="font-normal">
            Show done
          </Label>
        </div>
      </FilterBar>
      <div className="mb-6 sm:max-w-md">
        <InlineAddForm
          placeholder={addToName ? `Add a task to ${addToName}` : 'Add a task'}
          onAdd={(title) => createTask.mutateAsync({ data: { title, project_id: addTo } })}
        />
      </div>
      {isPending ? (
        <ListSkeleton />
      ) : error ? (
        <LoadError what="tasks" error={error} onRetry={refetch} />
      ) : tasks.length === 0 ? (
        filtered ? (
          <EmptyState icon={ListTodo} title="No tasks match this filter" />
        ) : (
          <EmptyState
            icon={ListTodo}
            title={showDone ? 'No tasks yet' : 'Nothing to do'}
            description="Tasks live in a project or on their own. A project's first open task is its next step."
          />
        )
      ) : (
        <div className="grid gap-6">
          {groupByProject(tasks).map((group) => (
            <section key={group.project?.id ?? NO_PROJECT}>
              <h2 className="mb-1 text-sm font-medium">
                {group.project ? (
                  <Link to={`/projects/${group.project.id}?tab=tasks`} className="hover:underline">
                    {group.project.name}
                  </Link>
                ) : (
                  'No project'
                )}
              </h2>
              <div className="-mx-3">
                {group.tasks.map((task) => (
                  <TaskRow key={task.id} task={task} />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  )
}
