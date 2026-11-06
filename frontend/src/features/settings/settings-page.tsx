import { useGetHealth } from '@/api/generated/health/health'
import { PageHeader } from '@/components/page-header'
import { Separator } from '@/components/ui/separator'
import { LocationTreeEditor } from '@/features/locations/location-tree-editor'
import { ShopManager } from '@/features/shops/shop-manager'
import { TagManager } from '@/features/tags/tag-manager'
import { McpSetting } from './mcp-setting'
import { StaleSetting } from './stale-setting'

function SystemStatus() {
  const { data, error, isPending } = useGetHealth()
  const status = isPending
    ? 'Checking…'
    : error
      ? `Unreachable (${error.message})`
      : `API ${data.status}, database ${data.database}`
  return (
    <section>
      <h2 className="text-lg font-semibold">System</h2>
      <p className="mt-1 text-sm text-muted-foreground">{status}</p>
    </section>
  )
}

export function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" />
      <div className="grid gap-8">
        <LocationTreeEditor />
        <Separator />
        <TagManager />
        <Separator />
        <ShopManager />
        <Separator />
        <StaleSetting />
        <Separator />
        <McpSetting />
        <Separator />
        <SystemStatus />
      </div>
    </>
  )
}
