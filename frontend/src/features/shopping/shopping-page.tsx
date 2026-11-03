import { ShoppingCart } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function ShoppingPage() {
  return (
    <>
      <PageHeader title="Shopping" description="Everything low, out or needed, by location." />
      <EmptyState
        icon={ShoppingCart}
        title="Nothing here yet"
        description="Coming in build step 5."
      />
    </>
  )
}
