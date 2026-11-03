import type { ItemSummary } from '@/api/generated/model'

/**
 * Orders items so children follow their parent, with a depth for indenting.
 * A child whose parent isn't in the list (e.g. filtered out) shows at the top level.
 */
export function nestItems(items: ItemSummary[]): { item: ItemSummary; depth: number }[] {
  const ids = new Set(items.map((item) => item.id))
  const children = new Map<number, ItemSummary[]>()
  const roots: ItemSummary[] = []
  for (const item of items) {
    if (item.parent_id != null && ids.has(item.parent_id)) {
      children.set(item.parent_id, [...(children.get(item.parent_id) ?? []), item])
    } else {
      roots.push(item)
    }
  }
  const nested: { item: ItemSummary; depth: number }[] = []
  const walk = (list: ItemSummary[], depth: number) => {
    for (const item of list) {
      nested.push({ item, depth })
      walk(children.get(item.id) ?? [], depth + 1)
    }
  }
  walk(roots, 0)
  return nested
}

/** The item and everything below it, e.g. to stop it being picked as its own parent. */
export function subtreeIds(items: ItemSummary[], itemId: number): Set<number> {
  const ids = new Set([itemId])
  let grew = true
  while (grew) {
    grew = false
    for (const item of items) {
      if (item.parent_id != null && ids.has(item.parent_id) && !ids.has(item.id)) {
        ids.add(item.id)
        grew = true
      }
    }
  }
  return ids
}
