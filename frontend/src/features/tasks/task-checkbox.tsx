import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

type Props = {
  done: boolean
  onToggle: () => void
  'aria-label': string
  className?: string
}

/** A round tick box for tasks. */
export function TaskCheckbox({ done, onToggle, className, ...rest }: Props) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={done}
      onClick={onToggle}
      className={cn(
        'flex size-5 shrink-0 items-center justify-center rounded-full border-2 border-muted-foreground/40 transition-colors hover:border-primary focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none',
        done && 'border-primary bg-primary text-primary-foreground',
        className,
      )}
      {...rest}
    >
      {done && <Check className="size-3" strokeWidth={3} />}
    </button>
  )
}
