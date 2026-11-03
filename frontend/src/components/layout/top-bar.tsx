import { Inbox, LibraryBig, Menu, Plus, Search } from 'lucide-react'
import { Link } from 'react-router'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { notes, settings } from './nav'

// Search, quick-add and the inbox count arrive in build step 8.
const COMING_SOON = 'Coming soon'

export function TopBar() {
  return (
    <header className="sticky top-0 z-10 flex h-14 items-center gap-2 border-b bg-background/95 px-4 backdrop-blur md:px-8">
      <Link to="/" className="flex items-center gap-2 font-semibold md:hidden">
        <LibraryBig className="size-5 text-primary" />
        Shelf-help
      </Link>

      <Button
        variant="outline"
        className="hidden w-64 justify-start text-muted-foreground md:flex"
        disabled
        title={COMING_SOON}
      >
        <Search />
        Search…
        <kbd className="ml-auto text-xs">Ctrl K</kbd>
      </Button>

      <div className="ml-auto flex items-center gap-1">
        <Button variant="ghost" size="icon" className="md:hidden" disabled title={COMING_SOON}>
          <Search />
          <span className="sr-only">Search</span>
        </Button>
        <Button variant="ghost" size="icon" asChild>
          <Link to="/inbox">
            <Inbox />
            <span className="sr-only">Inbox</span>
          </Link>
        </Button>
        <Button className="hidden md:flex" disabled title={COMING_SOON}>
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
    </header>
  )
}
