import { NotebookPen } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function NotesPage() {
  return (
    <>
      <PageHeader title="Notes" description="All notes, with or without a project." />
      <EmptyState
        icon={NotebookPen}
        title="Nothing here yet"
        description="Coming in build step 6."
      />
    </>
  )
}
