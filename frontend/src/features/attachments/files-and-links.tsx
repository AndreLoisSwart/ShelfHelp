import type { OwnerType } from '@/api/generated/model'
import { LinkList } from '@/features/links/link-list'
import { AttachmentList } from './attachment-list'

/** Files and links together, as shown on projects, items and notes. */
export function FilesAndLinks({ ownerType, ownerId }: { ownerType: OwnerType; ownerId: number }) {
  return (
    <div className="grid gap-8">
      <AttachmentList ownerType={ownerType} ownerId={ownerId} />
      <LinkList ownerType={ownerType} ownerId={ownerId} />
    </div>
  )
}
