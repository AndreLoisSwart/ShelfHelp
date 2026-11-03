import { Inbox } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function InboxPage() {
  return (
    <>
      <PageHeader title="Inbox" description="Quick-added records waiting to be sorted." />
      <EmptyState icon={Inbox} title="Nothing here yet" description="Coming in build step 8." />
    </>
  )
}
