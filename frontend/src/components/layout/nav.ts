import {
  FolderKanban,
  House,
  NotebookPen,
  Package,
  Settings,
  ShoppingCart,
  type LucideIcon,
} from 'lucide-react'

export type NavItem = { to: string; label: string; icon: LucideIcon }

export const home: NavItem = { to: '/', label: 'Home', icon: House }
export const projects: NavItem = { to: '/projects', label: 'Projects', icon: FolderKanban }
export const items: NavItem = { to: '/items', label: 'Items', icon: Package }
export const notes: NavItem = { to: '/notes', label: 'Notes', icon: NotebookPen }
export const shopping: NavItem = { to: '/shopping', label: 'Shopping', icon: ShoppingCart }
export const settings: NavItem = { to: '/settings', label: 'Settings', icon: Settings }

// Desktop sidebar, top to bottom. Settings sits apart at the bottom.
export const sidebarNav = [home, projects, items, notes, shopping]
