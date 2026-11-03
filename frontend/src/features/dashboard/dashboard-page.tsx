import { House } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function DashboardPage() {
  return (
    <>
      <PageHeader title="Home" description="Active projects, running low and stale projects." />
      <EmptyState icon={House} title="Nothing here yet" description="Coming in build step 9." />
    </>
  )
}
