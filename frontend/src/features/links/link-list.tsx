import { ExternalLink, Plus, Trash2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import {
  useCreateLink,
  useDeleteLink,
  useListLinks,
  useUpdateLink,
} from '@/api/generated/links/links'
import type { OwnerType } from '@/api/generated/model'
import { EditableText } from '@/components/editable-text'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { domainOf } from '@/lib/format'

type Props = { ownerType: OwnerType; ownerId: number }

function AddLinkForm({ ownerType, ownerId }: Props) {
  const createLink = useCreateLink()
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return
    createLink.mutate(
      { data: { owner_type: ownerType, owner_id: ownerId, url, title } },
      {
        onSuccess: () => {
          setUrl('')
          setTitle('')
        },
      },
    )
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-2 sm:flex-row">
      <Input
        type="url"
        inputMode="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://…"
        aria-label="Link address"
        className="sm:flex-[2]"
      />
      <Input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Title (optional)"
        aria-label="Link title"
        maxLength={200}
        className="sm:flex-1"
      />
      <Button type="submit" variant="outline" disabled={!url.trim() || createLink.isPending}>
        <Plus />
        Add link
      </Button>
    </form>
  )
}

/** The web links of one project, item or note. */
export function LinkList({ ownerType, ownerId }: Props) {
  const { data: links = [] } = useListLinks({ owner_type: ownerType, owner_id: ownerId })
  const updateLink = useUpdateLink()
  const deleteLink = useDeleteLink()

  return (
    <section>
      <h2 className="mb-2 text-sm font-medium">Links</h2>
      {links.length > 0 && (
        <ul className="-mx-3 mb-3 divide-y">
          {links.map((link) => (
            <li key={link.id} className="flex items-center gap-1 px-1 py-1">
              <Button variant="ghost" size="icon-sm" asChild>
                {/* Only http(s) links are accepted by the API. */}
                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`Open ${link.title || link.url}`}
                >
                  <ExternalLink />
                </a>
              </Button>
              <div className="min-w-0 flex-1">
                <EditableText
                  value={link.title}
                  onSave={(title) => updateLink.mutate({ linkId: link.id, data: { title } })}
                  allowEmpty
                  placeholder={domainOf(link.url)}
                  aria-label={`Title of ${link.url}`}
                  className="text-sm font-medium placeholder:text-foreground"
                />
                <div className="truncate px-2 text-xs text-muted-foreground">{link.url}</div>
              </div>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={`Delete link ${link.title || link.url}`}
                onClick={() => deleteLink.mutate({ linkId: link.id })}
              >
                <Trash2 />
              </Button>
            </li>
          ))}
        </ul>
      )}
      <AddLinkForm ownerType={ownerType} ownerId={ownerId} />
    </section>
  )
}
