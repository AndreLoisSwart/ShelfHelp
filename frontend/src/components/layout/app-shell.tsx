import { Outlet } from 'react-router'
import { QuickAddProvider } from '@/features/inbox/quick-add'
import { BottomBar } from './bottom-bar'
import { Sidebar } from './sidebar'
import { TopBar } from './top-bar'

// Desktop: sidebar plus top bar. Mobile: top bar plus bottom bar.
export function AppShell() {
  return (
    <QuickAddProvider>
      <div className="flex min-h-svh">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar />
          <main className="mx-auto w-full max-w-5xl flex-1 px-4 pt-6 pb-24 md:px-8 md:pb-8">
            <Outlet />
          </main>
        </div>
        <BottomBar />
      </div>
    </QuickAddProvider>
  )
}
