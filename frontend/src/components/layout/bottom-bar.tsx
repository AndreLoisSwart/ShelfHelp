import { Plus } from 'lucide-react'
import { NavLink } from 'react-router'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { home, items, projects, shopping, type NavItem } from './nav'

function BottomLink({ item }: { item: NavItem }) {
  return (
    <NavLink
      to={item.to}
      end={item.to === '/'}
      className={({ isActive }) =>
        cn(
          'flex flex-1 flex-col items-center gap-1 py-2 text-xs text-muted-foreground',
          isActive && 'text-primary',
        )
      }
    >
      <item.icon className="size-5" />
      {item.label}
    </NavLink>
  )
}

export function BottomBar() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-10 flex items-center border-t bg-background pb-[env(safe-area-inset-bottom)] md:hidden">
      <BottomLink item={home} />
      <BottomLink item={projects} />
      <div className="flex flex-1 justify-center">
        {/* Quick-add arrives in build step 8. */}
        <Button size="icon-lg" className="rounded-full" disabled title="Coming soon">
          <Plus />
          <span className="sr-only">Add</span>
        </Button>
      </div>
      <BottomLink item={items} />
      <BottomLink item={shopping} />
    </nav>
  )
}
