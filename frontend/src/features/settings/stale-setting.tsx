import { useGetSettings, useUpdateSettings } from '@/api/generated/settings/settings'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { daysAsWeeks } from '@/lib/format'

const WEEKS = [1, 2, 3, 4, 6, 8, 12]

/** How long an active or paused project can go untouched before Home calls it out. */
export function StaleSetting() {
  const { data } = useGetSettings()
  const updateSettings = useUpdateSettings()
  const options = WEEKS.map((weeks) => weeks * 7)
  // Keep a value set some other way (the API allows any number of days) visible.
  if (data && !options.includes(data.stale_after_days)) {
    options.push(data.stale_after_days)
    options.sort((a, b) => a - b)
  }

  return (
    <section>
      <h2 className="text-lg font-semibold">Projects</h2>
      <p className="mt-1 mb-3 text-sm text-muted-foreground" id="stale-after-label">
        An active or paused project counts as gone quiet when it hasn't been touched for:
      </p>
      <ToggleGroup
        type="single"
        variant="outline"
        aria-labelledby="stale-after-label"
        value={data ? String(data.stale_after_days) : ''}
        onValueChange={(next) =>
          next && updateSettings.mutate({ data: { stale_after_days: Number(next) } })
        }
        className="flex-wrap justify-start"
        disabled={!data}
      >
        {options.map((days) => (
          <ToggleGroupItem key={days} value={String(days)}>
            {daysAsWeeks(days)}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    </section>
  )
}
