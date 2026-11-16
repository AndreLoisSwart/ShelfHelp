import type { TaskReadiness } from '@/api/generated/model'

/** Linked items on hand, out of all of them. Null when nothing is linked. */
export function itemReadiness({ ready, total }: TaskReadiness) {
  return total === 0 ? null : `${ready} of ${total} items on hand`
}
