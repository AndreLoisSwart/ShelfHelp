import { Check, ShoppingCart } from 'lucide-react'
import { Link, useSearchParams } from 'react-router'
import { toast } from 'sonner'
import { useUpdateItem } from '@/api/generated/items/items'
import type { ShoppingItem, ShoppingList } from '@/api/generated/model'
import { useGetShoppingLists } from '@/api/generated/shopping/shopping'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'
import { StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useLocationTree } from '@/features/locations/location-tree'
import { LoadError } from '@/components/load-error'
import { ListSkeleton } from '@/components/loading'

const tabValue = (list: ShoppingList) => (list.zone ? String(list.zone.id) : 'unassigned')

type RowProps = { item: ShoppingItem; onGotIt: () => void; busy: boolean }

function ShoppingRow({ item, onGotIt, busy }: RowProps) {
  const { byId: locations } = useLocationTree()
  // The zone is the tab, so show only where in it the item lives.
  const path = item.location_id == null ? undefined : locations.get(item.location_id)?.path
  const where = path?.split(' › ').slice(1).join(' › ')

  return (
    <div className="flex items-center gap-2">
      <Link
        to={`/items/${item.id}`}
        className="flex min-w-0 flex-1 items-center gap-3 rounded-md px-3 py-2.5 hover:bg-muted/60"
      >
        <div className="min-w-0 flex-1">
          <div className="truncate font-medium">{item.name}</div>
          {(where || item.projects.length > 0) && (
            <div className="mt-0.5 truncate text-xs text-muted-foreground">
              {[where, item.projects.length && `for ${item.projects.map((p) => p.name).join(', ')}`]
                .filter(Boolean)
                .join(' · ')}
            </div>
          )}
        </div>
        <StatusBadge status={item.status} />
      </Link>
      <Button variant="outline" onClick={onGotIt} disabled={busy}>
        <Check />
        Got it
      </Button>
    </div>
  )
}

export function ShoppingPage() {
  const { data: lists, isPending, error, refetch } = useGetShoppingLists()
  const [params, setParams] = useSearchParams()
  // Here rather than in the row: the row disappears once its item is got, and Undo
  // must still work after that.
  const updateItem = useUpdateItem()

  const gotIt = (item: ShoppingItem) => {
    const previous = item.status
    updateItem.mutate(
      { itemId: item.id, data: { status: 'have' } },
      {
        onSuccess: () =>
          toast(`Got ${item.name}`, {
            // Longer than the default 4s, to leave time to spot a mis-tap.
            duration: 8000,
            action: {
              label: 'Undo',
              onClick: () => updateItem.mutate({ itemId: item.id, data: { status: previous } }),
            },
          }),
      },
    )
  }

  if (isPending || error) {
    return (
      <>
        <PageHeader title="Shopping" />
        {isPending ? (
          <ListSkeleton />
        ) : (
          <LoadError what="the shopping list" error={error} onRetry={refetch} />
        )}
      </>
    )
  }

  if (lists.length === 0) {
    return (
      <>
        <PageHeader title="Shopping" />
        {/* Every zone gets a list, even an empty one, so this means there are no zones. */}
        <EmptyState
          icon={ShoppingCart}
          title="Nothing to buy"
          description="Items marked low, out or need to get show up here, with a list per zone. Add zones such as Home and Workshop in Settings."
        >
          <Button variant="outline" asChild>
            <Link to="/settings">Open Settings</Link>
          </Button>
        </EmptyState>
      </>
    )
  }

  const requested = params.get('zone')
  const current = lists.some((list) => tabValue(list) === requested)
    ? requested!
    : tabValue(lists.find((list) => list.items.length > 0) ?? lists[0])

  return (
    <>
      <PageHeader title="Shopping" description="Everything low, out or needed, by zone." />
      <Tabs value={current} onValueChange={(zone) => setParams({ zone }, { replace: true })}>
        <TabsList className="h-auto flex-wrap justify-start">
          {lists.map((list) => (
            <TabsTrigger key={tabValue(list)} value={tabValue(list)}>
              {list.zone?.name ?? 'Unassigned'}
              <span className="text-xs text-muted-foreground">{list.items.length}</span>
            </TabsTrigger>
          ))}
        </TabsList>
        {lists.map((list) => (
          <TabsContent key={tabValue(list)} value={tabValue(list)} className="mt-4">
            {list.items.length > 0 ? (
              <div className="-mx-3 divide-y">
                {list.items.map((item) => (
                  <ShoppingRow
                    key={item.id}
                    item={item}
                    onGotIt={() => gotIt(item)}
                    busy={updateItem.isPending}
                  />
                ))}
              </div>
            ) : (
              <EmptyState icon={ShoppingCart} title="Nothing to get here" />
            )}
          </TabsContent>
        ))}
      </Tabs>
    </>
  )
}
