import { X } from 'lucide-react'
import type { TagRef } from '@/api/generated/model'
import { useCreateTag, useListTags } from '@/api/generated/tags/tags'
import { EntityPicker } from '@/components/entity-picker'
import { Badge } from '@/components/ui/badge'

type Props = { value: TagRef[]; onChange: (tagIds: number[]) => void }

/** Assigned tags with remove buttons, plus a picker that can create new tags. */
export function TagEditor({ value, onChange }: Props) {
  const { data: tags = [] } = useListTags()
  const createTag = useCreateTag()
  const ids = value.map((tag) => tag.id)
  const add = (id: number) => onChange([...ids, id])

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {value.map((tag) => (
        <Badge key={tag.id} variant="secondary" className="h-7 gap-1 pr-1 font-normal">
          {tag.name}
          <button
            type="button"
            onClick={() => onChange(ids.filter((id) => id !== tag.id))}
            className="rounded-full p-0.5 hover:bg-foreground/10"
            aria-label={`Remove tag ${tag.name}`}
          >
            <X />
          </button>
        </Badge>
      ))}
      <EntityPicker
        options={tags.filter((t) => !ids.includes(t.id)).map((t) => ({ id: t.id, label: t.name }))}
        value={undefined}
        onChange={(id) => id != null && add(id)}
        placeholder="Add tag"
        searchPlaceholder="Find or create a tag…"
        onCreate={(name) =>
          createTag.mutate({ data: { name } }, { onSuccess: (tag) => add(tag.id) })
        }
        className="h-7 w-auto"
      />
    </div>
  )
}
