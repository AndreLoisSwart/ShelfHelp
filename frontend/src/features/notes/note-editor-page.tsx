import { NotebookPen, Trash2 } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router'
import { errorMessage } from '@/api/fetcher'
import type { NoteUpdate } from '@/api/generated/model'
import { useDeleteNote, useGetNote, useUpdateNote } from '@/api/generated/notes/notes'
import { useListProjects } from '@/api/generated/projects/projects'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { EditableText } from '@/components/editable-text'
import { EmptyState } from '@/components/empty-state'
import { EntityPicker } from '@/components/entity-picker'
import { LazyMarkdownEditor } from '@/components/lazy-markdown-editor'
import { NotFound } from '@/components/not-found'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/format'
import { useAutosave } from '@/lib/use-autosave'

export function NoteEditorPage() {
  const noteId = Number(useParams().id)
  const navigate = useNavigate()
  const { data: note, error, isPending } = useGetNote(noteId)
  const { data: projects = [] } = useListProjects()
  const updateNote = useUpdateNote()
  const deleteNote = useDeleteNote()
  const save = (data: NoteUpdate) => updateNote.mutate({ noteId, data })
  const body = useAutosave((body_md) => save({ body_md }))

  if (isPending) return null
  if (error) {
    if (error.status === 404 || error.status === 422) return <NotFound />
    return (
      <EmptyState
        icon={NotebookPen}
        title="Couldn't load this note"
        description={errorMessage(error)}
      />
    )
  }

  return (
    <>
      <div className="flex items-start gap-2">
        <EditableText
          value={note.title}
          onSave={(title) => save({ title })}
          aria-label="Title"
          className="-ml-2 text-2xl font-semibold tracking-tight"
        />
        <ConfirmDialog
          title={`Delete ${note.title}?`}
          description="This can't be undone."
          onConfirm={() =>
            deleteNote.mutate(
              { noteId },
              {
                onSuccess: () =>
                  navigate(note.project ? `/projects/${note.project.id}?tab=notes` : '/notes', {
                    replace: true,
                  }),
              },
            )
          }
          trigger={
            <Button variant="ghost" size="icon" className="mt-1" aria-label="Delete note">
              <Trash2 />
            </Button>
          }
        />
      </div>

      <div className="mt-2 mb-5 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm">
        <EntityPicker
          options={projects.map((p) => ({ id: p.id, label: p.name }))}
          value={note.project?.id ?? null}
          onChange={(project_id) => save({ project_id })}
          placeholder="No project"
          noneLabel="No project"
          searchPlaceholder="Find a project…"
          className="h-8 w-auto max-w-full"
        />
        {note.project && (
          <Link
            to={`/projects/${note.project.id}?tab=notes`}
            className="text-muted-foreground underline-offset-4 hover:underline"
          >
            Open project
          </Link>
        )}
        <span className="ml-auto text-xs text-muted-foreground" aria-live="polite">
          {body.dirty || updateNote.isPending ? 'Saving…' : 'Saved'}
        </span>
      </div>

      <LazyMarkdownEditor
        key={note.id}
        value={note.body_md}
        onChange={body.schedule}
        onBlur={body.flush}
        aria-label="Note"
        placeholder="Write here. Markdown shortcuts work: # heading, - list, [ ] checkbox."
      />

      <p className="mt-6 text-xs text-muted-foreground">
        Added {formatDate(note.created_at)} · Updated {formatDate(note.updated_at)}
      </p>
    </>
  )
}
