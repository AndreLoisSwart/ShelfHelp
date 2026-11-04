import { Inbox } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

/** On a detail page, for a record still in the inbox. Done clears the flag. */
export function InboxNotice({ onDone, className }: { onDone: () => void; className?: string }) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-lg bg-primary/10 py-1.5 pr-1.5 pl-3 text-sm',
        className,
      )}
    >
      <Inbox className="size-4 shrink-0 text-primary" />
      In the inbox, waiting to be sorted
      <Button size="sm" variant="outline" className="ml-auto" onClick={onDone}>
        Done
      </Button>
    </div>
  )
}
