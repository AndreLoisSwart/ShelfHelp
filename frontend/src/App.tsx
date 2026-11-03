import { Route, Routes } from 'react-router'
import { AppShell } from '@/components/layout/app-shell'
import { NotFound } from '@/components/not-found'
import { DashboardPage } from '@/features/dashboard/dashboard-page'
import { InboxPage } from '@/features/inbox/inbox-page'
import { ItemDetailPage } from '@/features/items/item-detail-page'
import { ItemsPage } from '@/features/items/items-page'
import { NoteEditorPage } from '@/features/notes/note-editor-page'
import { NotesPage } from '@/features/notes/notes-page'
import { ProjectDetailPage } from '@/features/projects/project-detail-page'
import { ProjectsPage } from '@/features/projects/projects-page'
import { SettingsPage } from '@/features/settings/settings-page'
import { ShoppingPage } from '@/features/shopping/shopping-page'

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
