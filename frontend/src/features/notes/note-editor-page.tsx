import { NotebookPen } from 'lucide-react'
import { useParams } from 'react-router'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function NoteEditorPage() {
  const { id } = useParams()
  return (
    <>
      <PageHeader title={`Note ${id}`} />
      <EmptyState
        icon={NotebookPen}
        title="Nothing here yet"
        description="Coming in build step 6."
      />
    </>
  )
}
