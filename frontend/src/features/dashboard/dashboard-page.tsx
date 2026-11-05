import { ArrowRight, FolderKanban, House, MapPin, Plus } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import { errorMessage } from '@/api/fetcher'
import { useGetDashboard } from '@/api/generated/dashboard/dashboard'
import type { Dashboard, ProjectSummary, StaleProject } from '@/api/generated/model'
import { useUpdateProject } from '@/api/generated/projects/projects'
import { EditableText } from '@/components/editable-text'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'
import { ReadinessBar } from '@/components/readiness-bar'
import { StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { ItemRow } from '@/features/items/item-row'
import { useLocationTree } from '@/features/locations/location-tree'
import { daysAsWeeks, durationSince, timeAgo } from '@/lib/format'
import { cn } from '@/lib/utils'
import { useQuickAdd } from '@/features/inbox/use-quick-add'
import { CardsSkeleton } from '@/components/loading'

type SectionProps = {
  title: string
  description?: string
  link?: { to: string; label: string }
  children: ReactNode
}

function Section({ title, description, link, children }: SectionProps) {
  return (
    <section className="min-w-0">
      <div className="mb-3 flex items-end justify-between gap-3">
        <div>
          <h2 className="font-semibold">{title}</h2>
          {description && <p className="text-xs text-muted-foreground">{description}</p>}
        </div>
        {link && (
          <Link
            to={link.to}
            className="flex shrink-0 items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            {link.label}
            <ArrowRight className="size-3.5" />
          </Link>
        )}
      </div>
      {children}
    </section>
  )
}

function Quiet({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">{children}</p>
  )
}

/** Like ProjectCard, but the next step is edited right here instead of linking through. */
function ActiveProjectCard({ project, stale }: { project: ProjectSummary; stale: boolean }) {
  const updateProject = useUpdateProject()
  return (
    <div className="rounded-lg border bg-card p-3 text-card-foreground">
      <Link to={`/projects/${project.id}`} className="leading-snug font-medium hover:underline">
        {project.name}
      </Link>
      <div className="mt-1 flex items-baseline gap-1 text-sm">
        <span className="shrink-0 text-muted-foreground">Next:</span>
        <EditableText
          value={project.next_step}
          onSave={(next_step) =>
            updateProject.mutate({ projectId: project.id, data: { next_step } })
          }
          aria-label={`Next step for ${project.name}`}
          placeholder="Add a next step"
          allowEmpty
          className="-my-1 min-w-0 flex-1"
        />
      </div>
      <ReadinessBar readiness={project.readiness} className="mt-2" />
      <p className={cn('mt-2 text-xs text-muted-foreground', stale && 'text-status-orange')}>
        Touched {timeAgo(project.last_touched_at)}
      </p>
    </div>
  )
}

function ActiveProjects({ dashboard }: { dashboard: Dashboard }) {
  const stale = new Set(dashboard.stale.map((project) => project.id))
  return (
    <Section title="Active projects" link={{ to: '/projects', label: 'All projects' }}>
      {dashboard.active.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="No active projects"
          description="Move a project to Active on the board and it shows up here with its next step."
        >
          <Button variant="outline" asChild>
            <Link to="/projects">Open projects</Link>
          </Button>
        </EmptyState>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {dashboard.active.map((project) => (
            <ActiveProjectCard key={project.id} project={project} stale={stale.has(project.id)} />
          ))}
        </div>
      )}
    </Section>
  )
}

function RunningLow({ dashboard }: { dashboard: Dashboard }) {
  const { byId: locations } = useLocationTree()
  const more = dashboard.running_low_total - dashboard.running_low.length
  return (
    <Section title="Running low" link={{ to: '/shopping', label: 'Shopping' }}>
      {dashboard.running_low.length === 0 ? (
        <Quiet>Nothing is low or out.</Quiet>
      ) : (
        <div className="-mx-3">
          {dashboard.running_low.map((item) => (
            <ItemRow
              key={item.id}
              item={item}
              locationPath={
                item.location_id == null ? undefined : locations.get(item.location_id)?.path
              }
            />
          ))}
          {more > 0 && (
            <Link
              to="/shopping"
              className="block px-3 py-2 text-sm text-muted-foreground hover:text-foreground"
            >
              and {more} more on the shopping list
            </Link>
          )}
        </div>
      )}
    </Section>
  )
}

function StaleRow({ project }: { project: StaleProject }) {
  return (
    <li>
      <Link
        to={`/projects/${project.id}`}
        className="-mx-3 flex items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-muted/60"
      >
        <span className="min-w-0 truncate">{project.name}</span>
        {project.status === 'paused' && <StatusBadge status={project.status} />}
        <span className="ml-auto shrink-0 text-xs text-status-orange tabular-nums">
          {durationSince(project.last_touched_at)}
        </span>
      </Link>
    </li>
  )
}

function Stale({ dashboard }: { dashboard: Dashboard }) {
  const threshold = daysAsWeeks(dashboard.stale_after_days)
  return (
    <Section title="Gone quiet" description={`Active or paused, untouched for over ${threshold}`}>
      {dashboard.stale.length === 0 ? (
        <Quiet>Everything active has been touched in the last {threshold}.</Quiet>
      ) : (
        <ul>
          {dashboard.stale.map((project) => (
            <StaleRow key={project.id} project={project} />
          ))}
        </ul>
      )}
    </Section>
  )
}

/** For a fresh install: zones come first, since items and shopping lists hang off them. */
function GettingStarted() {
  const { roots, isPending } = useLocationTree()
  const quickAdd = useQuickAdd()
  if (isPending || roots.length > 0) return null
  return (
    <section className="rounded-lg border bg-card p-4">
      <h2 className="font-semibold">Getting started</h2>
      <ol className="mt-2 grid list-decimal gap-1 pl-5 text-sm text-muted-foreground">
        <li>
          Add your zones, the top-level places things live, such as Home and Workshop. Each gets its
          own shopping list.
        </li>
        <li>Add items and projects, or capture anything quickly with the + button.</li>
        <li>Link items to projects to see how ready each project is.</li>
      </ol>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button asChild>
          <Link to="/settings">
            <MapPin />
            Add zones
          </Link>
        </Button>
        <Button variant="outline" onClick={quickAdd}>
          <Plus />
          Quick add
        </Button>
      </div>
    </section>
  )
}

export function DashboardPage() {
  const { data: dashboard, error, isPending } = useGetDashboard()
  const header = <PageHeader title="Home" />
  if (isPending) {
    return (
      <>
        {header}
        <CardsSkeleton />
      </>
    )
  }
  if (error) {
    return (
      <>
        {header}
        <EmptyState
          icon={House}
          title="Couldn't load the dashboard"
          description={errorMessage(error)}
        />
      </>
    )
  }
  return (
    <>
      {header}
      <div className="grid gap-10">
        <GettingStarted />
        <ActiveProjects dashboard={dashboard} />
        <div className="grid gap-10 md:grid-cols-2 md:gap-8">
          <RunningLow dashboard={dashboard} />
          <Stale dashboard={dashboard} />
        </div>
      </div>
    </>
  )
}
