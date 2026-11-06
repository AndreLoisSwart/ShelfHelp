import { toast } from 'sonner'
import {
  countItemsMissingTag,
  useTagItems,
  useUpdateLocation,
} from '@/api/generated/locations/locations'
import type { TagRef } from '@/api/generated/model'
import { TagEditor } from '@/features/tags/tag-editor'
import { plural } from '@/lib/format'
import type { LocationNode } from './location-tree'

/**
 * A location's tags. Items put there from now on get them; after adding one, offers to
 * tag the items already there too, since that's not done unasked.
 */
export function LocationTagEditor({ node }: { node: LocationNode }) {
  const updateLocation = useUpdateLocation()
  const tagItems = useTagItems()

  const offerToTagExisting = async (tag: TagRef) => {
    const { count } = await countItemsMissingTag(node.id, tag.id)
    if (count === 0) return
    toast(`Also tag the ${plural(count, 'item')} already in ${node.name} as ${tag.name}?`, {
      duration: 10000,
      action: {
        label: 'Tag them',
        onClick: () =>
          tagItems.mutate(
            { locationId: node.id, tagId: tag.id },
            { onSuccess: ({ count }) => toast.success(`Tagged ${plural(count, 'item')}`) },
          ),
      },
    })
  }

  const change = (tagIds: number[]) => {
    const before = new Set(node.tags.map((tag) => tag.id))
    updateLocation.mutate(
      { locationId: node.id, data: { tag_ids: tagIds } },
      {
        onSuccess: (location) => {
          for (const tag of location.tags) {
            if (!before.has(tag.id)) void offerToTagExisting(tag).catch(() => {})
          }
        },
      },
    )
  }

  return <TagEditor value={node.tags} onChange={change} />
}
