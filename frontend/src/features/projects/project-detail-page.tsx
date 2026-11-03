import { FolderKanban } from 'lucide-react'
import { useParams } from 'react-router'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function ProjectDetailPage() {
  const { id } = useParams()
  return (
    <>
      <PageHeader title={`Project ${id}`} />
      <EmptyState
        icon={FolderKanban}
        title="Nothing here yet"
        description="Coming in build step 4."
      />
    </>
  )
}
