import { Inbox, Plus } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import { toast } from 'sonner'
import { useGetInbox } from '@/api/generated/inbox/inbox'
import { useUpdateItem } from '@/api/generated/items/items'
import type {
  ItemSummary,
  ItemUpdate,
  NoteSummary,
  NoteUpdate,
  ProjectSummary,
  ProjectUpdate,
} from '@/api/generated/model'
import { useUpdateNote } from '@/api/generated/notes/notes'
import { useListProjects, useUpdateProject } from '@/api/generated/projects/projects'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { ItemStatusToggle } from '@/features/items/item-status-toggle'
import { LocationTreeSelect } from '@/features/locations/location-tree-select'
import { ProjectStatusToggle } from '@/features/projects/project-status-toggle'
import { TagEditor } from '@/features/tags/tag-editor'
import { errorMessage } from '@/api/fetcher'
import { useQuickAdd } from './use-quick-add'

// Saves live in the page, not the cards: Done removes the card, and Undo must still work.
type Save<T> = (data: T, onSuccess?: () => void) => void

/** Clears the inbox flag, with a moment to undo it. */
function done(name: string, save: Save<{ in_inbox: boolean }>) {
  save({ in_inbox: false }, () =>
    toast(`Sorted ${name}`, { action: { label: 'Undo', onClick: () => save({ in_inbox: true }) } }),
  )
}

type CardProps = { title: string; to: string; onDone: () => void; children: ReactNode }

function InboxCard({ title, to, onDone, children }: CardProps) {
  return (
    <li className="grid gap-3 rounded-lg border p-4">
      <div className="flex items-start gap-2">
        <Link to={to} className="min-w-0 pt-1 font-medium break-words hover:underline">
          {title}
        </Link>
        <Button size="sm" variant="outline" className="ml-auto shrink-0" onClick={onDone}>
          Done
        </Button>
      </div>
      {children}
    </li>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid gap-1.5 sm:grid-cols-[5.5rem_1fr] sm:items-center sm:gap-3">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="min-w-0">{children}</div>
    </div>
  )
}

function ItemCard({ item, save }: { item: ItemSummary; save: Save<ItemUpdate> }) {
  return (
    <InboxCard title={item.name} to={`/items/${item.id}`} onDone={() => done(item.name, save)}>
      <Field label="Status">
        <ItemStatusToggle value={item.status} onChange={(status) => save({ status })} />
      </Field>
      <Field label="Location">
        <LocationTreeSelect
          value={item.location_id}
          onChange={(location_id) => save({ location_id })}
          noneLabel="No location"
          className="w-full sm:w-72"
        />
      </Field>
      <Field label="Tags">
        <TagEditor value={item.tags} onChange={(tag_ids) => save({ tag_ids })} />
      </Field>
    </InboxCard>
  )
}

function ProjectCard({ project, save }: { project: ProjectSummary; save: Save<ProjectUpdate> }) {
  return (
    <InboxCard
      title={project.name}
      to={`/projects/${project.id}`}
      onDone={() => done(project.name, save)}
    >
      <Field label="Status">
        <ProjectStatusToggle value={project.status} onChange={(status) => save({ status })} />
      </Field>
      <Field label="Tags">
        <TagEditor value={project.tags} onChange={(tag_ids) => save({ tag_ids })} />
      </Field>
    </InboxCard>
  )
}

type NoteCardProps = { note: NoteSummary; projects: ProjectSummary[]; save: Save<NoteUpdate> }

function NoteCard({ note, projects, save }: NoteCardProps) {
  return (
    <InboxCard title={note.title} to={`/notes/${note.id}`} onDone={() => done(note.title, save)}>
      {note.excerpt && <p className="line-clamp-2 text-sm text-muted-foreground">{note.excerpt}</p>}
      <Field label="Project">
        <EntityPicker
          options={projects.map((p) => ({ id: p.id, label: p.name }))}
          value={note.project?.id ?? null}
          onChange={(project_id) => save({ project_id })}
          placeholder="No project"
          noneLabel="No project"
          searchPlaceholder="Find a project…"
          className="w-full sm:w-72"
        />
      </Field>
    </InboxCard>
  )
}

function Section({
  title,
  count,
  children,
}: {
  title: string
  count: number
  children: ReactNode
}) {
  if (count === 0) return null
  return (
    <section className="grid gap-3">
      <h2 className="text-sm font-medium">
        {title} <span className="text-muted-foreground tabular-nums">{count}</span>
      </h2>
      <ul className="grid gap-3">{children}</ul>
    </section>
  )
}

export function InboxPage() {
  const { data: inbox, error, isPending } = useGetInbox()
  const { data: projects = [] } = useListProjects()
  const quickAdd = useQuickAdd()
  const updateItem = useUpdateItem()
  const updateProject = useUpdateProject()
  const updateNote = useUpdateNote()

  const header = (
    <PageHeader
      title="Inbox"
      description="Quick-added records waiting to be sorted. Fill in what you know, then tap Done."
    />
  )
  if (isPending) return header
  if (error) {
    return (
      <>
        {header}
        <EmptyState
          icon={Inbox}
          title="Couldn't load the inbox"
          description={errorMessage(error)}
        />
      </>
    )
  }

  const total = inbox.items.length + inbox.projects.length + inbox.notes.length
  return (
    <>
      {header}
      {total === 0 ? (
        <EmptyState
          icon={Inbox}
          title="All sorted"
          description="Anything you quick-add lands here until you sort it."
        >
          <Button onClick={quickAdd}>
            <Plus />
            Quick add
          </Button>
        </EmptyState>
      ) : (
        <div className="grid gap-8">
          <Section title="Items" count={inbox.items.length}>
            {inbox.items.map((item) => (
              <ItemCard
                key={item.id}
                item={item}
                save={(data, onSuccess) =>
                  updateItem.mutate({ itemId: item.id, data }, { onSuccess })
                }
              />
            ))}
          </Section>
          <Section title="Projects" count={inbox.projects.length}>
            {inbox.projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                save={(data, onSuccess) =>
                  updateProject.mutate({ projectId: project.id, data }, { onSuccess })
                }
              />
            ))}
          </Section>
          <Section title="Notes" count={inbox.notes.length}>
            {inbox.notes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                projects={projects}
                save={(data, onSuccess) =>
                  updateNote.mutate({ noteId: note.id, data }, { onSuccess })
                }
              />
            ))}
          </Section>
        </div>
      )}
    </>
  )
}
