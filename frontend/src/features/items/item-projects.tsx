import { X } from 'lucide-react'
import { Link } from 'react-router'
import type { ItemDetail, ItemProjectOut, Requirement } from '@/api/generated/model'
import {
  useCreateProject,
  useLinkProjectItem,
  useListProjects,
  useUnlinkProjectItem,
} from '@/api/generated/projects/projects'
import { EntityPicker } from '@/components/entity-picker'
import { StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { FINISHED_PROJECT_STATUSES, REQUIREMENT_LABELS } from '@/lib/statuses'

function LinkedProject({ itemId, link }: { itemId: number; link: ItemProjectOut }) {
  const linkItem = useLinkProjectItem()
  const unlinkItem = useUnlinkProjectItem()
  const { project } = link

  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 py-2 pr-1 pl-3">
      <Link
        to={`/projects/${project.id}?tab=items`}
        className="flex min-w-0 flex-1 basis-48 items-center gap-2 hover:underline"
      >
        <span className="truncate font-medium">{project.name}</span>
        <StatusBadge status={project.status} />
      </Link>
      <div className="flex items-center gap-1">
        <ToggleGroup
          type="single"
          variant="outline"
          size="sm"
          value={link.requirement}
          onValueChange={(next) =>
            next &&
            linkItem.mutate({
              projectId: project.id,
              itemId,
              data: { requirement: next as Requirement, note: link.note },
            })
          }
          aria-label={`How much ${project.name} needs it`}
        >
          {(Object.keys(REQUIREMENT_LABELS) as Requirement[]).map((requirement) => (
            <ToggleGroupItem key={requirement} value={requirement}>
              {REQUIREMENT_LABELS[requirement]}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label={`Unlink from ${project.name}`}
          onClick={() => unlinkItem.mutate({ projectId: project.id, itemId })}
        >
          <X />
        </Button>
      </div>
      {link.note && <p className="w-full text-xs text-muted-foreground">{link.note}</p>}
    </div>
  )
}

/** The item page's "Used in": linking to projects from this side too. */
export function ItemProjects({ item }: { item: ItemDetail }) {
  const { data: projects = [] } = useListProjects()
  const createProject = useCreateProject()
  const linkItem = useLinkProjectItem()

  const linkedIds = new Set(item.projects.map((link) => link.project.id))
  const link = (projectId: number) =>
    linkItem.mutate({ projectId, itemId: item.id, data: { requirement: 'required', note: '' } })

  return (
    <div className="grid gap-3">
      {item.projects.length > 0 && (
        <div className="-mx-3 divide-y">
          {item.projects.map((link) => (
            <LinkedProject key={link.project.id} itemId={item.id} link={link} />
          ))}
        </div>
      )}
      <EntityPicker
        options={projects
          .filter((p) => !linkedIds.has(p.id) && !FINISHED_PROJECT_STATUSES.includes(p.status))
          .map((p) => ({ id: p.id, label: p.name }))}
        value={undefined}
        onChange={(id) => id != null && link(id)}
        placeholder="Link to a project"
        searchPlaceholder="Find or create a project…"
        onCreate={(name) =>
          createProject.mutate({ data: { name } }, { onSuccess: (project) => link(project.id) })
        }
        className="w-full sm:w-80"
      />
    </div>
  )
}
