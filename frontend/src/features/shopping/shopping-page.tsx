import { Check, ShoppingCart } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link, useSearchParams } from 'react-router'
import { toast } from 'sonner'
import { useUpdateItem } from '@/api/generated/items/items'
import type { ShoppingItem, ShoppingList } from '@/api/generated/model'
import { useGetShoppingLists } from '@/api/generated/shopping/shopping'
import { useListShops } from '@/api/generated/shops/shops'
import { EmptyState } from '@/components/empty-state'
import { PageHeader } from '@/components/page-header'
import { StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { useLocationTree } from '@/features/locations/location-tree'
import { LoadError } from '@/components/load-error'
import { ListSkeleton } from '@/components/loading'

const tabValue = (list: ShoppingList) => (list.zone ? String(list.zone.id) : 'unassigned')

type RowProps = {
  item: ShoppingItem
  onGotIt: () => void
  busy: boolean
  /** Show the zone too, for rows not already under their zone's heading. */
  withZone?: boolean
  /** Show which shops sell it (not needed once filtered to one shop). */
  withShops?: boolean
}

function ShoppingRow({ item, onGotIt, busy, withZone, withShops }: RowProps) {
  const { byId: locations } = useLocationTree()
  const path = item.location_id == null ? undefined : locations.get(item.location_id)?.path
  // Under a zone tab or heading, show only where in the zone the item lives.
  const where = withZone ? path : path?.split(' › ').slice(1).join(' › ')
  const details = [
    where,
    withShops && item.shops.length > 0 && `at ${item.shops.map((s) => s.name).join(', ')}`,
    item.projects.length > 0 && `for ${item.projects.map((p) => p.name).join(', ')}`,
  ].filter(Boolean)

  return (
    <div className="flex items-center gap-2">
      <Link
        to={`/items/${item.id}`}
        className="flex min-w-0 flex-1 items-center gap-3 rounded-md px-3 py-2.5 hover:bg-muted/60"
      >
        <div className="min-w-0 flex-1">
          <div className="truncate font-medium">{item.name}</div>
          {details.length > 0 && (
            <div className="mt-0.5 truncate text-xs text-muted-foreground">
              {details.join(' · ')}
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

type SectionProps = { title: string; note?: string; children: ReactNode }

function Section({ title, note, children }: SectionProps) {
  return (
    <section className="mt-6 first:mt-0">
      <h2 className="text-sm font-medium">
        {title}
        {note && <span className="ml-2 font-normal text-muted-foreground">{note}</span>}
      </h2>
      <div className="mt-1 -mx-3 divide-y">{children}</div>
    </section>
  )
}

export function ShoppingPage() {
  const [params, setParams] = useSearchParams()
  const { data: shops = [] } = useListShops()
  const shop = shops.find((s) => String(s.id) === params.get('shop'))
  // Filtered here rather than with the API's shop_id, so switching shops is instant.
  const { data: lists, isPending, error, refetch } = useGetShoppingLists()
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

  const row = (item: ShoppingItem, extra?: Partial<RowProps>) => (
    <ShoppingRow
      key={item.id}
      item={item}
      onGotIt={() => gotIt(item)}
      busy={updateItem.isPending}
      {...extra}
    />
  )

  // Keeps the other parameter, so switching shops remembers the zone tab and back.
  const setParam = (key: string, value: string | null) => {
    const next = new URLSearchParams(params)
    if (value == null) next.delete(key)
    else next.set(key, value)
    setParams(next, { replace: true })
  }

  const shopFilter = shops.length > 0 && (
    <ToggleGroup
      type="single"
      variant="outline"
      size="sm"
      value={shop ? String(shop.id) : 'any'}
      onValueChange={(value) => value && setParam('shop', value === 'any' ? null : value)}
      aria-label="Shop"
      className="mb-4 flex-wrap justify-start"
    >
      <ToggleGroupItem value="any">Any shop</ToggleGroupItem>
      {shops.map((s) => (
        <ToggleGroupItem key={s.id} value={String(s.id)}>
          {s.name}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  )

  if (shop) {
    // At a shop, everything to get there across all zones, then what has no shop set yet.
    const atShop = lists
      .map((list) => ({
        list,
        items: list.items.filter((item) => item.shops.some((s) => s.id === shop.id)),
      }))
      .filter(({ items }) => items.length > 0)
    const unset = lists.flatMap((list) => list.items.filter((item) => item.shops.length === 0))
    return (
      <>
        <PageHeader
          title="Shopping"
          description={`What to get at ${shop.name}, across all zones.`}
        />
        {shopFilter}
        {atShop.length === 0 && unset.length === 0 ? (
          <EmptyState icon={ShoppingCart} title={`Nothing to get at ${shop.name}`} />
        ) : (
          <>
            {atShop.length === 0 && (
              <p className="mb-6 text-sm text-muted-foreground">
                Nothing marked as sold at {shop.name}.
              </p>
            )}
            {atShop.map(({ list, items }) => (
              <Section key={tabValue(list)} title={list.zone?.name ?? 'Unassigned'}>
                {items.map((item) => row(item))}
              </Section>
            ))}
            {unset.length > 0 && (
              <Section title="No shop set" note="could be from anywhere">
                {unset.map((item) => row(item, { withZone: true }))}
              </Section>
            )}
          </>
        )}
      </>
    )
  }

  return (
    <>
      <PageHeader title="Shopping" description="Everything low, out or needed, by zone." />
      {shopFilter}
      <Tabs value={current} onValueChange={(zone) => setParam('zone', zone)}>
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
                {list.items.map((item) => row(item, { withShops: true }))}
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
