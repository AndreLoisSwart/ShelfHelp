import { Suspense, useState } from 'react'
import { Outlet, useLocation } from 'react-router'
import { ErrorBoundary } from '@/components/error-boundary'
import { DetailSkeleton } from '@/components/loading'
import { QuickAddProvider } from '@/features/inbox/quick-add'
import { BottomBar } from './bottom-bar'
import { ConnectionBanner } from './connection-banner'
import { PageWidthContext } from './page-width'
import { Sidebar } from './sidebar'
import { TopBar } from './top-bar'
import { cn } from '@/lib/utils'

// Desktop: sidebar plus top bar. Mobile: top bar plus bottom bar.
export function AppShell() {
  const { pathname } = useLocation()
  const [wide, setWide] = useState(false)
  return (
    <QuickAddProvider>
      <PageWidthContext.Provider value={setWide}>
        <div className="flex min-h-svh">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <TopBar />
            <ConnectionBanner />
            <main
              className={cn(
                'mx-auto w-full flex-1 px-4 pt-6 pb-24 md:px-8 md:pb-8',
                // Wide pages still stop short of very wide screens, where columns would sprawl.
                wide ? 'max-w-[100rem]' : 'max-w-5xl',
              )}
            >
              {/* Keyed by path: a crash on one page clears when you move to another. */}
              <ErrorBoundary key={pathname}>
                <Suspense fallback={<DetailSkeleton />}>
                  <Outlet />
                </Suspense>
              </ErrorBoundary>
            </main>
          </div>
          <BottomBar />
        </div>
      </PageWidthContext.Provider>
    </QuickAddProvider>
  )
}
