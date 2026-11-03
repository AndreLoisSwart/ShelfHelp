import type { ReactNode } from 'react'
import { useSearchParams } from 'react-router'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export type DetailTab = { value: string; label: string; content: ReactNode }

/** A detail page header followed by tabs. The open tab is kept in the URL (?tab=). */
export function DetailLayout({ header, tabs }: { header: ReactNode; tabs: DetailTab[] }) {
  const [params, setParams] = useSearchParams()
  const requested = params.get('tab')
  const current = tabs.some((tab) => tab.value === requested) ? requested! : tabs[0].value

  const select = (value: string) => {
    const next = new URLSearchParams(params)
    if (value === tabs[0].value) next.delete('tab')
    else next.set('tab', value)
    setParams(next, { replace: true })
  }

  return (
    <>
      {header}
      <Tabs value={current} onValueChange={select} className="mt-8">
        <TabsList>
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>
        {tabs.map((tab) => (
          <TabsContent key={tab.value} value={tab.value} className="mt-4">
            {tab.content}
          </TabsContent>
        ))}
      </Tabs>
    </>
  )
}
