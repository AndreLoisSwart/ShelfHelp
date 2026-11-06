import type { ShopRef } from '@/api/generated/model'
import { useCreateShop, useListShops } from '@/api/generated/shops/shops'
import { ChipPicker } from '@/components/chip-picker'

type Props = { value: ShopRef[]; onChange: (shopIds: number[]) => void }

/** The shops an item can be bought from, plus a picker that can create new shops. */
export function ShopEditor({ value, onChange }: Props) {
  const { data: shops = [] } = useListShops()
  const createShop = useCreateShop()
  return (
    <ChipPicker
      noun="shop"
      value={value}
      options={shops}
      onChange={onChange}
      onCreate={(name, add) =>
        createShop.mutate({ data: { name } }, { onSuccess: (shop) => add(shop.id) })
      }
    />
  )
}
