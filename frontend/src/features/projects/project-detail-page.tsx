import { FolderKanban, Plus, Trash2 } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router'
import { errorMessage } from '@/api/fetcher'
import type { ProjectUpdate } from '@/api/generated/model'
import {
  useDeleteProject,
  useGetProject,
  useUpdateProject,
} from '@/api/generated/projects/projects'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DetailLayout } from '@/components/detail-layout'
import { EditableText } from '@/components/editable-text'
import { EmptyState } from '@/components/empty-state'
import { LazyMarkdownEditor } from '@/components/lazy-markdown-editor'
import { NotFound } from '@/components/not-found'
import { ReadinessBar } from '@/components/readiness-bar'
import { Button } from '@/components/ui/button'
import { FilesAndLinks } from '@/features/attachments/files-and-links'
import { InboxNotice } from '@/features/inbox/inbox-notice'
import { NewNoteDialog } from '@/features/notes/new-note-dialog'
import { NoNotesYet, NotesList } from '@/features/notes/notes-list'
import { TagEditor } from '@/features/tags/tag-editor'
import { NextStep } from '@/features/tasks/next-step'
import { ProjectTasksTab } from '@/features/tasks/project-tasks-tab'
import { formatDate, plural, timeAgo } from '@/lib/format'
import { useAutosave } from '@/lib/use-autosave'
import { ProjectItemsTab } from './project-items-tab'
import { ProjectStatusToggle } from './project-status-toggle'
import { DetailSkeleton } from '@/components/loading'

export function ProjectDetailPage() {
  const projectId = Number(useParams().id)
  const navigate = useNavigate()
  const { data: project, error, isPending } = useGetProject(projectId)
  const updateProject = useUpdateProject()
  const deleteProject = useDeleteProject()
  const description = useAutosave((description_md) =>
    updateProject.mutate({ projectId, data: { description_md } }),
  )

  if (isPending) return <DetailSkeleton />
  if (error) {
    if (error.status === 404 || error.status === 422) return <NotFound />
    return (
      <EmptyState
        icon={FolderKanban}
        title="Couldn't load this project"
        description={errorMessage(error)}
      />
    )
  }

  const save = (data: ProjectUpdate) => updateProject.mutate({ projectId, data })

  const header = (
    <>
      <div className="flex items-start gap-2">
        <EditableText
          value={project.name}
          onSave={(name) => save({ name })}
          aria-label="Name"
          className="-ml-2 text-2xl font-semibold tracking-tight"
        />
        <ConfirmDialog
          title={`Delete ${project.name}?`}
          description="Its notes are kept, without a project. Its item links are removed."
          onConfirm={() =>
            deleteProject.mutate(
              { projectId },
              { onSuccess: () => navigate('/projects', { replace: true }) },
            )
          }
          trigger={
            <Button variant="ghost" size="icon" className="mt-1" aria-label="Delete project">
              <Trash2 />
            </Button>
          }
        />
      </div>
      <p className="mb-5 text-xs text-muted-foreground">
        Touched {timeAgo(project.last_touched_at)} · Added {formatDate(project.created_at)}
      </p>
      {project.in_inbox && (
        <InboxNotice onDone={() => save({ in_inbox: false })} className="mb-5" />
      )}
      <ProjectStatusToggle value={project.status} onChange={(status) => save({ status })} />
      <ReadinessBar readiness={project.readiness} detailed className="mt-5 max-w-md" />
      <div className="mt-5">
        <div className="mb-1 flex items-baseline gap-2">
          <h2 className="text-sm font-medium">Next step</h2>
          {project.task_counts.open + project.task_counts.done > 0 && (
            <Link to="?tab=tasks" className="text-xs text-muted-foreground hover:text-foreground">
              {plural(project.task_counts.open, 'task')} to do · {project.task_counts.done} done
            </Link>
          )}
        </div>
        <NextStep
          projectId={projectId}
          projectName={project.name}
          nextTask={project.next_task}
          className="text-base"
        />
      </div>
    </>
  )

  return (
    <DetailLayout
      header={header}
      tabs={[
        {
          value: 'overview',
          label: 'Overview',
          content: (
            <div className="grid gap-6">
              <div>
                <h2 className="mb-2 text-sm font-medium">Tags</h2>
                <TagEditor value={project.tags} onChange={(tag_ids) => save({ tag_ids })} />
                {project.suggested_tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                    <span>Its items are tagged:</span>
                    {project.suggested_tags.map((tag) => (
                      <Button
                        key={tag.id}
                        variant="ghost"
                        size="xs"
                        onClick={() =>
                          save({ tag_ids: [...project.tags.map((t) => t.id), tag.id] })
                        }
                        aria-label={`Add tag ${tag.name}`}
                        className="text-muted-foreground"
                      >
                        <Plus />
                        {tag.name}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
              <div>
                <h2 className="mb-2 text-sm font-medium">Description</h2>
                <LazyMarkdownEditor
                  key={project.id}
                  value={project.description_md}
                  onChange={description.schedule}
                  onBlur={description.flush}
                  aria-label="Description"
                  placeholder="What is this project about?"
                />
              </div>
            </div>
          ),
        },
        {
          value: 'tasks',
          label: 'Tasks',
          content: <ProjectTasksTab projectId={projectId} />,
        },
        {
          value: 'notes',
          label: 'Notes',
          content: (
            <div className="grid gap-4">
              <NewNoteDialog
                projectId={projectId}
                trigger={
                  <Button variant="outline" className="w-fit">
                    <Plus />
                    New note
                  </Button>
                }
              />
              <NotesList
                params={{ project_id: projectId }}
                showProject={false}
                empty={
                  <NoNotesYet description="Plans, measurements and checklists for this project." />
                }
              />
            </div>
          ),
        },
        {
          value: 'items',
          label: 'Items',
          content: <ProjectItemsTab projectId={projectId} />,
        },
        {
          value: 'files',
          label: 'Files & links',
          content: <FilesAndLinks ownerType="project" ownerId={projectId} />,
        },
      ]}
    />
  )
}
