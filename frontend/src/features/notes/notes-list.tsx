import { NotebookPen } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { ListNotesParams, NoteSummary } from '@/api/generated/model'
import { useListNotes } from '@/api/generated/notes/notes'
import { EmptyState } from '@/components/empty-state'
import { timeAgo } from '@/lib/format'

type Props = {
  params?: ListNotesParams
  /** Off inside a project, where every note belongs to it. */
  showProject?: boolean
  empty: ReactNode
}

function NoteRow({ note, showProject }: { note: NoteSummary; showProject: boolean }) {
  return (
    <Link to={`/notes/${note.id}`} className="block rounded-md px-3 py-2.5 hover:bg-muted/60">
      <div className="truncate font-medium">{note.title}</div>
      {note.excerpt && (
        <p className="mt-0.5 line-clamp-2 text-sm text-muted-foreground">{note.excerpt}</p>
      )}
      <div className="mt-1 text-xs text-muted-foreground">
        {showProject && note.project && `${note.project.name} · `}
        Updated {timeAgo(note.updated_at)}
      </div>
    </Link>
  )
}

/** Notes, most recently updated first. Used by the Notes page and the project Notes tab. */
export function NotesList({ params, showProject = true, empty }: Props) {
  const { data: notes, isPending } = useListNotes(params)
  if (isPending) return null
  if (!notes?.length) return empty
  return (
    <div className="-mx-3 divide-y">
      {notes.map((note) => (
        <NoteRow key={note.id} note={note} showProject={showProject} />
      ))}
    </div>
  )
}

type NoNotesProps = { description: string; children?: ReactNode }

export function NoNotesYet({ description, children }: NoNotesProps) {
  return (
    <EmptyState icon={NotebookPen} title="No notes yet" description={description}>
      {children}
    </EmptyState>
  )
}
