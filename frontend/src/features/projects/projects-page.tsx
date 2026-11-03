import { FolderKanban } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function ProjectsPage() {
  return (
    <>
      <PageHeader title="Projects" description="Everything from someday ideas to active builds." />
      <EmptyState
        icon={FolderKanban}
        title="Nothing here yet"
        description="Coming in build step 4."
      />
    </>
  )
}
