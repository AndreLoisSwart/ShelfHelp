import { NotebookPen, Plus } from 'lucide-react'
import { useSearchParams } from 'react-router'
import { useListProjects } from '@/api/generated/projects/projects'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { FilterBar } from '@/components/filter-bar'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { NewNoteDialog } from './new-note-dialog'
import { NoNotesYet, NotesList } from './notes-list'

// A pseudo-project in the filter, for notes that don't belong to one.
const NO_PROJECT = 0

const newNoteButton = (
  <Button>
    <Plus />
    New note
  </Button>
)

export function NotesPage() {
  const [params, setParams] = useSearchParams()
  const { data: projects = [] } = useListProjects()
  const filter = params.has('project') ? Number(params.get('project')) : null

  return (
    <>
      <PageHeader title="Notes" actions={<NewNoteDialog trigger={newNoteButton} />} />
      <FilterBar>
        <EntityPicker
          options={[
            { id: NO_PROJECT, label: 'No project' },
            ...projects.map((p) => ({ id: p.id, label: p.name })),
          ]}
          value={filter}
          onChange={(id) =>
            setParams(id === null ? {} : { project: String(id) }, { replace: true })
          }
          placeholder="All notes"
          noneLabel="All notes"
          searchPlaceholder="Find a project…"
          className="w-full sm:w-56"
        />
      </FilterBar>
      <NotesList
        params={
          filter === null
            ? undefined
            : filter === NO_PROJECT
              ? { no_project: true }
              : { project_id: filter }
        }
        showProject={filter === null}
        empty={
          filter === null ? (
            <NoNotesYet description="Plans, measurements, checklists. Written in markdown.">
              <NewNoteDialog trigger={newNoteButton} />
            </NoNotesYet>
          ) : (
            <EmptyState icon={NotebookPen} title="No notes match this filter" />
          )
        }
      />
    </>
  )
}
