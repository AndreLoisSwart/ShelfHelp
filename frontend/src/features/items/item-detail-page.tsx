import { Package } from 'lucide-react'
import { useParams } from 'react-router'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

export function ItemDetailPage() {
  const { id } = useParams()
  return (
    <>
      <PageHeader title={`Item ${id}`} />
      <EmptyState icon={Package} title="Nothing here yet" description="Coming in build step 3." />
    </>
  )
}
