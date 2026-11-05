import { keepPreviousData } from '@tanstack/react-query'
import { FolderKanban, Inbox, NotebookPen, Package, Plus } from 'lucide-react'
import { useEffect, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import { useSearch } from '@/api/generated/search/search'
import { StatusBadge } from '@/components/status-badge'
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import { home, items, notes, projects, settings, shopping } from '@/components/layout/nav'
import { useQuickAdd } from '@/features/inbox/use-quick-add'
import type { Status } from '@/lib/statuses'
import { useBackToClose } from '@/lib/use-back-to-close'
import { splitMarks } from './marks'

const PAGES = [
  home,
  projects,
  items,
  notes,
  shopping,
  { to: '/inbox', label: 'Inbox', icon: Inbox },
  settings,
]

/** Text from the search API, with the matched words highlighted. */
function Highlighted({ text }: { text: string }) {
  return splitMarks(text).map((part, i) =>
    part.marked ? (
      <mark key={i} className="rounded-sm bg-primary/15 text-foreground">
        {part.text}
      </mark>
    ) : (
      <span key={i}>{part.text}</span>
    ),
  )
}

type Hit = { id: number; title: string; snippet: string; status?: Status }

type HitItemProps = { value: string; hit: Hit; icon: ReactNode; onSelect: () => void }

function HitItem({ value, hit, icon, onSelect }: HitItemProps) {
  return (
    <CommandItem value={value} onSelect={onSelect} className="items-start">
      {icon}
      <div className="grid min-w-0 flex-1 gap-0.5">
        <span className="truncate">
          <Highlighted text={hit.title} />
        </span>
        {hit.snippet.trim() && (
          <span className="line-clamp-2 text-xs text-muted-foreground">
            <Highlighted text={hit.snippet} />
          </span>
        )}
      </div>
      {hit.status && <StatusBadge status={hit.status} />}
    </CommandItem>
  )
}

function useDebounced(value: string, ms: number) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), ms)
    return () => clearTimeout(timer)
  }, [value, ms])
  return debounced
}

type Props = { open: boolean; onOpenChange: (open: boolean) => void }

/** Search across projects, items and notes. With nothing typed, jumps to pages. */
export function SearchPalette({ open, onOpenChange }: Props) {
  const navigate = useNavigate()
  const quickAdd = useQuickAdd()
  const [query, setQuery] = useState('')
  const q = useDebounced(query.trim(), 150)
  const { data } = useSearch(
    { q },
    { query: { enabled: open && q !== '', placeholderData: keepPreviousData } },
  )

  const changeOpen = (next: boolean) => {
    onOpenChange(next)
    if (!next) setQuery('')
  }
  const afterClose = useBackToClose(open, () => changeOpen(false))
  const go = (to: string) => {
    changeOpen(false)
    afterClose(() => navigate(to))
  }

  const results = query.trim() && q ? data : undefined
  const groups = results
    ? [
        { key: 'projects', heading: 'Projects', hits: results.projects, icon: FolderKanban },
        { key: 'items', heading: 'Items', hits: results.items, icon: Package },
        { key: 'notes', heading: 'Notes', hits: results.notes, icon: NotebookPen },
      ]
    : []

  return (
    <CommandDialog
      open={open}
      onOpenChange={changeOpen}
      title="Search"
      description="Search projects, items and notes"
      className="max-md:top-4 sm:max-w-lg"
    >
      {/* Results come from the server already ranked, so cmdk mustn't filter or sort. */}
      <Command shouldFilter={false}>
        <CommandInput
          value={query}
          onValueChange={setQuery}
          placeholder="Search projects, items and notes…"
          maxLength={200}
        />
        <CommandList className="max-h-[min(28rem,60svh)]">
          {query.trim() === '' ? (
            <>
              <CommandGroup heading="Go to">
                {PAGES.map((page) => (
                  <CommandItem key={page.to} value={page.to} onSelect={() => go(page.to)}>
                    <page.icon />
                    {page.label}
                  </CommandItem>
                ))}
              </CommandGroup>
              <CommandGroup heading="Actions">
                <CommandItem
                  value="quick-add"
                  onSelect={() => {
                    changeOpen(false)
                    afterClose(quickAdd)
                  }}
                >
                  <Plus />
                  Quick add
                </CommandItem>
              </CommandGroup>
            </>
          ) : (
            <>
              {results && <CommandEmpty>No matches</CommandEmpty>}
              {groups.map(
                ({ key, heading, hits, icon: Icon }) =>
                  hits.length > 0 && (
                    <CommandGroup key={key} heading={heading}>
                      {hits.map((hit) => (
                        <HitItem
                          key={hit.id}
                          value={`${key}-${hit.id}`}
                          hit={hit}
                          icon={<Icon className="mt-0.5" />}
                          onSelect={() => go(`/${key}/${hit.id}`)}
                        />
                      ))}
                    </CommandGroup>
                  ),
              )}
            </>
          )}
        </CommandList>
      </Command>
    </CommandDialog>
  )
}
