import type { ItemStatus } from '@/api/generated/model'

// Status colours, see docs/pages.md. Project statuses join in build step 4.
// Class names are written out in full so Tailwind can find them.

export const ITEM_STATUSES: ItemStatus[] = ['have', 'low', 'out', 'need']

export const ITEM_STATUS_LABELS: Record<ItemStatus, string> = {
  have: 'Have',
  low: 'Low',
  out: 'Out',
  need: 'Need to get',
}

export const ITEM_STATUS_TONES: Record<ItemStatus, string> = {
  have: 'bg-status-green/15 text-status-green',
  low: 'bg-status-amber/15 text-status-amber',
  out: 'bg-status-red/15 text-status-red',
  need: 'bg-status-violet/15 text-status-violet',
}

/** For toggles: the tone applies only while the toggle is on. */
export const ITEM_STATUS_ACTIVE_TONES: Record<ItemStatus, string> = {
  have: 'data-[state=on]:bg-status-green/15 data-[state=on]:text-status-green',
  low: 'data-[state=on]:bg-status-amber/15 data-[state=on]:text-status-amber',
  out: 'data-[state=on]:bg-status-red/15 data-[state=on]:text-status-red',
  need: 'data-[state=on]:bg-status-violet/15 data-[state=on]:text-status-violet',
}
