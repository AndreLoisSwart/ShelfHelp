import { lazy } from 'react'
import { Route, Routes } from 'react-router'
import { AppShell } from '@/components/layout/app-shell'
import { NotFound } from '@/components/not-found'
import { DashboardPage } from '@/features/dashboard/dashboard-page'

// Home loads with the app; other pages load when first opened, so the first visit
// downloads less (it matters on mobile data over the VPN).
const page = <K extends string>(load: () => Promise<Record<K, React.ComponentType>>, name: K) =>
  lazy(() => load().then((module) => ({ default: module[name] })))

const InboxPage = page(() => import('@/features/inbox/inbox-page'), 'InboxPage')
const ItemDetailPage = page(() => import('@/features/items/item-detail-page'), 'ItemDetailPage')
const ItemsPage = page(() => import('@/features/items/items-page'), 'ItemsPage')
const NoteEditorPage = page(() => import('@/features/notes/note-editor-page'), 'NoteEditorPage')
const NotesPage = page(() => import('@/features/notes/notes-page'), 'NotesPage')
const ProjectDetailPage = page(
  () => import('@/features/projects/project-detail-page'),
  'ProjectDetailPage',
)
const ProjectsPage = page(() => import('@/features/projects/projects-page'), 'ProjectsPage')
const SettingsPage = page(() => import('@/features/settings/settings-page'), 'SettingsPage')
const ShoppingPage = page(() => import('@/features/shopping/shopping-page'), 'ShoppingPage')

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="projects/:id" element={<ProjectDetailPage />} />
        <Route path="items" element={<ItemsPage />} />
        <Route path="items/:id" element={<ItemDetailPage />} />
        <Route path="notes" element={<NotesPage />} />
        <Route path="notes/:id" element={<NoteEditorPage />} />
        <Route path="shopping" element={<ShoppingPage />} />
        <Route path="inbox" element={<InboxPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
