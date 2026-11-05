import { useQueryClient } from '@tanstack/react-query'
import { Columns3, FolderKanban, List, Plus, X } from 'lucide-react'
import { useSearchParams } from 'react-router'
import type { ProjectStatus, ProjectSummary } from '@/api/generated/model'
import {
  getListProjectsQueryKey,
  useListProjects,
  useUpdateProject,
} from '@/api/generated/projects/projects'
import { useListTags } from '@/api/generated/tags/tags'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { FilterBar } from '@/components/filter-bar'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import {
  FINISHED_PROJECT_STATUSES,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUSES,
  STATUS_ACTIVE_TONES,
} from '@/lib/statuses'
import { usePersistentState } from '@/lib/use-persistent-state'
import { NewProjectDialog } from './new-project-dialog'
import { ProjectBoard } from './project-board'
import { ProjectCard } from './project-card'
import { LoadError } from '@/components/load-error'
import { CardsSkeleton } from '@/components/loading'

const VIEWS = ['board', 'list'] as const

const newProjectButton = (
  <Button>
    <Plus />
    New project
  </Button>
)

export function ProjectsPage() {
  const queryClient = useQueryClient()
  const updateProject = useUpdateProject()
  const [view, setView] = usePersistentState('projects-view', 'board', VIEWS)

  // Filters live in the URL, so they survive going back from a project.
  const [params, setParams] = useSearchParams()
  const tagId = params.has('tag') ? Number(params.get('tag')) : undefined
  const showFinished = params.get('finished') === '1'
  const visibleStatuses = PROJECT_STATUSES.filter(
    (status) => showFinished || !FINISHED_PROJECT_STATUSES.includes(status),
  )
  // The status filter is for the list; on the board the columns already split by status.
  const pickedStatuses = (params.getAll('status') as ProjectStatus[]).filter((status) =>
    visibleStatuses.includes(status),
  )
  const filtered = tagId !== undefined || pickedStatuses.length > 0

  const setFilter = (key: string, values: string[]) => {
    const next = new URLSearchParams(params)
    next.delete(key)
    values.forEach((value) => next.append(key, value))
    setParams(next, { replace: true })
  }

  const clearFilters = () => {
    const next = new URLSearchParams(params)
    next.delete('tag')
    next.delete('status')
    setParams(next, { replace: true })
  }

  const listParams = { tag_id: tagId !== undefined ? [tagId] : undefined }
  const { data: projects, isPending, error, refetch } = useListProjects(listParams)
  const { data: tags = [] } = useListTags()

  const shown = (projects ?? []).filter((project) =>
    (view === 'list' && pickedStatuses.length ? pickedStatuses : visibleStatuses).includes(
      project.status,
    ),
  )

  const move = (projectId: number, status: ProjectStatus) => {
    // Move the card straight away rather than waiting for the server.
    queryClient.setQueryData<ProjectSummary[]>(getListProjectsQueryKey(listParams), (old) =>
      old?.map((project) => (project.id === projectId ? { ...project, status } : project)),
    )
    updateProject.mutate(
      { projectId, data: { status } },
      { onError: () => queryClient.invalidateQueries() },
    )
  }

  return (
    <>
      <PageHeader title="Projects" actions={<NewProjectDialog trigger={newProjectButton} />} />

      <FilterBar>
        <ToggleGroup
          type="single"
          variant="outline"
          value={view}
          onValueChange={(next) => next && setView(next as (typeof VIEWS)[number])}
          aria-label="View"
        >
          <ToggleGroupItem value="board" aria-label="Board">
            <Columns3 />
            Board
          </ToggleGroupItem>
          <ToggleGroupItem value="list" aria-label="List">
            <List />
            List
          </ToggleGroupItem>
        </ToggleGroup>
        <EntityPicker
          options={tags.map((tag) => ({ id: tag.id, label: tag.name }))}
          value={tagId ?? null}
          onChange={(id) => setFilter('tag', id === null ? [] : [String(id)])}
          placeholder="All tags"
          noneLabel="All tags"
          searchPlaceholder="Find a tag…"
          className="w-40"
        />
        <div className="flex items-center gap-2">
          <Switch
            id="show-finished"
            checked={showFinished}
            onCheckedChange={(checked) => setFilter('finished', checked ? ['1'] : [])}
          />
          <Label htmlFor="show-finished" className="font-normal">
            Show finished
          </Label>
        </div>
        {view === 'list' && (
          <ToggleGroup
            type="multiple"
            variant="outline"
            size="sm"
            value={pickedStatuses}
            onValueChange={(next) => setFilter('status', next)}
            className="flex-wrap"
            aria-label="Status"
          >
            {visibleStatuses.map((status) => (
              <ToggleGroupItem key={status} value={status} className={STATUS_ACTIVE_TONES[status]}>
                {PROJECT_STATUS_LABELS[status]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        )}
        {filtered && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X />
            Clear
          </Button>
        )}
      </FilterBar>

      {isPending ? (
        <CardsSkeleton />
      ) : error ? (
        <LoadError what="projects" error={error} onRetry={refetch} />
      ) : projects?.length === 0 && !filtered ? (
        <EmptyState
          icon={FolderKanban}
          title="No projects yet"
          description="Anything from a someday idea to an ongoing build."
        >
          <NewProjectDialog trigger={newProjectButton} />
        </EmptyState>
      ) : view === 'board' ? (
        <ProjectBoard projects={shown} statuses={visibleStatuses} onMove={move} />
      ) : shown.length ? (
        <div className="grid gap-2">
          {shown.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      ) : (
        <EmptyState icon={FolderKanban} title="No projects match these filters" />
      )}
    </>
  )
}
