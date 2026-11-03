import { Settings } from 'lucide-react'
import { useGetHealth } from '@/api/generated/health/health'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'

function SystemStatus() {
  const { data, error, isPending } = useGetHealth()
  const status = isPending
    ? 'Checking…'
    : error
      ? `Unreachable (${error.message})`
      : `API ${data.status}, database ${data.database}`
  return (
    <section className="mt-8">
      <h2 className="text-sm font-medium">System</h2>
      <p className="mt-1 text-sm text-muted-foreground">{status}</p>
    </section>
  )
}

export function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" description="Locations and tags." />
      <EmptyState
        icon={Settings}
        title="Nothing here yet"
        description="The location tree editor and tag management arrive in build step 3."
      />
      <SystemStatus />
    </>
  )
}
