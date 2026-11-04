import { Inbox, LibraryBig, Menu, Plus, Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { useGetInboxCount } from '@/api/generated/inbox/inbox'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useQuickAdd } from '@/features/inbox/use-quick-add'
import { SearchPalette } from '@/features/search/search-palette'
import { notes, settings } from './nav'

function InboxLink() {
  const { data } = useGetInboxCount()
  const count = data?.count ?? 0
  return (
    <Button variant="ghost" size="icon" className="relative" asChild>
      <Link to="/inbox">
        <Inbox />
        <span className="sr-only">Inbox{count > 0 && `, ${count} to sort`}</span>
        {count > 0 && (
          <span
            aria-hidden
            className="absolute -top-0.5 -right-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-medium text-primary-foreground tabular-nums"
          >
            {count > 99 ? '99+' : count}
          </span>
        )}
      </Link>
    </Button>
  )
}

export function TopBar() {
  const quickAdd = useQuickAdd()
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === 'k' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault()
        setSearching((open) => !open)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center gap-2 border-b bg-background/95 px-4 backdrop-blur md:px-8">
      <Link to="/" className="flex items-center gap-2 font-semibold md:hidden">
        <LibraryBig className="size-5 text-primary" />
        Shelf-help
      </Link>

      <Button
        variant="outline"
        className="hidden w-64 justify-start text-muted-foreground md:flex"
        onClick={() => setSearching(true)}
      >
        <Search />
        Search…
        <kbd className="ml-auto text-xs">Ctrl K</kbd>
      </Button>

      <div className="ml-auto flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setSearching(true)}
        >
          <Search />
          <span className="sr-only">Search</span>
        </Button>
        <InboxLink />
        <Button className="hidden md:flex" onClick={quickAdd}>
          <Plus />
          Add
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu />
              <span className="sr-only">More</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {[notes, settings].map((item) => (
              <DropdownMenuItem key={item.to} asChild>
                <Link to={item.to}>
                  <item.icon />
                  {item.label}
                </Link>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <SearchPalette open={searching} onOpenChange={setSearching} />
    </header>
  )
}
