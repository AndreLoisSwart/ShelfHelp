import type { ItemStatus, ProjectStatus } from '@/api/generated/model'

// Status colours, see docs/pages.md.
// Class names are written out in full so Tailwind can find them.

const NEUTRAL = 'bg-muted text-muted-foreground'
const NEUTRAL_ACTIVE = 'data-[state=on]:bg-muted data-[state=on]:text-foreground'

export const ITEM_STATUSES: ItemStatus[] = ['have', 'low', 'out', 'need']

export const ITEM_STATUS_LABELS: Record<ItemStatus, string> = {
  have: 'Have',
  low: 'Low',
  out: 'Out',
  need: 'Need to get',
}

export const PROJECT_STATUSES: ProjectStatus[] = [
  'someday',
  'planned',
  'active',
  'paused',
  'done',
  'abandoned',
]

/** Hidden on the board and in the list unless "Show finished" is on. */
export const FINISHED_PROJECT_STATUSES: ProjectStatus[] = ['done', 'abandoned']

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  someday: 'Someday',
  planned: 'Planned',
  active: 'Active',
  paused: 'Paused',
  done: 'Done',
  abandoned: 'Abandoned',
}

export type Status = ItemStatus | ProjectStatus

// Item and project status values don't overlap, so one map covers both.
export const STATUS_LABELS: Record<Status, string> = {
  ...ITEM_STATUS_LABELS,
  ...PROJECT_STATUS_LABELS,
}

export const STATUS_TONES: Record<Status, string> = {
  have: 'bg-status-green/15 text-status-green',
  low: 'bg-status-amber/15 text-status-amber',
  out: 'bg-status-red/15 text-status-red',
  need: 'bg-status-violet/15 text-status-violet',
  someday: NEUTRAL,
  planned: 'bg-status-violet/15 text-status-violet',
  active: 'bg-status-green/15 text-status-green',
  paused: 'bg-status-amber/15 text-status-amber',
  done: NEUTRAL,
  abandoned: NEUTRAL,
}

/** For toggles: the tone applies only while the toggle is on. */
export const STATUS_ACTIVE_TONES: Record<Status, string> = {
  have: 'data-[state=on]:bg-status-green/15 data-[state=on]:text-status-green',
  low: 'data-[state=on]:bg-status-amber/15 data-[state=on]:text-status-amber',
  out: 'data-[state=on]:bg-status-red/15 data-[state=on]:text-status-red',
  need: 'data-[state=on]:bg-status-violet/15 data-[state=on]:text-status-violet',
  someday: NEUTRAL_ACTIVE,
  planned: 'data-[state=on]:bg-status-violet/15 data-[state=on]:text-status-violet',
  active: 'data-[state=on]:bg-status-green/15 data-[state=on]:text-status-green',
  paused: 'data-[state=on]:bg-status-amber/15 data-[state=on]:text-status-amber',
  done: NEUTRAL_ACTIVE,
  abandoned: NEUTRAL_ACTIVE,
}
