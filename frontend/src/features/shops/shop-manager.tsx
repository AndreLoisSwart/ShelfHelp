import { Trash2 } from 'lucide-react'
import {
  useCreateShop,
  useDeleteShop,
  useListShops,
  useUpdateShop,
} from '@/api/generated/shops/shops'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { EditableText } from '@/components/editable-text'
import { InlineAddForm } from '@/components/inline-add-form'
import { Button } from '@/components/ui/button'
import { plural } from '@/lib/format'

export function ShopManager() {
  const { data: shops = [], isPending } = useListShops()
  const createShop = useCreateShop()
  const updateShop = useUpdateShop()
  const deleteShop = useDeleteShop()

  return (
    <section>
      <h2 className="text-lg font-semibold">Shops</h2>
      <p className="mt-1 mb-4 text-sm text-muted-foreground">
        Where items can be bought, to filter the shopping list by. Click a name to rename it.
      </p>
      {shops.length > 0 ? (
        <ul className="mb-4">
          {shops.map((shop) => (
            <li
              key={shop.id}
              className="flex items-center gap-2 rounded-md py-1 pr-1 hover:bg-muted/60"
            >
              <EditableText
                value={shop.name}
                onSave={(name) => updateShop.mutate({ shopId: shop.id, data: { name } })}
                aria-label={`Name of shop ${shop.name}`}
              />
              <span className="shrink-0 text-xs text-muted-foreground">
                {plural(shop.item_count, 'item')}
              </span>
              <ConfirmDialog
                title={`Delete the shop ${shop.name}?`}
                description={
                  shop.item_count > 0
                    ? `It will be removed from ${plural(shop.item_count, 'item')}.`
                    : undefined
                }
                onConfirm={() => deleteShop.mutate({ shopId: shop.id })}
                trigger={
                  <Button variant="ghost" size="icon-sm" aria-label={`Delete shop ${shop.name}`}>
                    <Trash2 />
                  </Button>
                }
              />
            </li>
          ))}
        </ul>
      ) : (
        !isPending && <p className="mb-4 text-sm text-muted-foreground">No shops yet.</p>
      )}
      <InlineAddForm
        placeholder="New shop"
        onAdd={(name) => createShop.mutateAsync({ data: { name } })}
      />
    </section>
  )
}
