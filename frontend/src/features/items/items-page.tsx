import { Package } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function ItemsPage() {
  return (
    <>
      <PageHeader title="Items" description="Tools, components, consumables and household goods." />
      <EmptyState icon={Package} title="Nothing here yet" description="Coming in build step 3." />
    </>
  )
}
