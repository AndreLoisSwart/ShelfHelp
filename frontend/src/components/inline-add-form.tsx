import { Plus } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

type Props = {
  placeholder: string
  /** Resolves once saved, which clears the field. */
  onAdd: (name: string) => Promise<unknown>
  onCancel?: () => void
  autoFocus?: boolean
}

export function InlineAddForm({ placeholder, onAdd, onCancel, autoFocus }: Props) {
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const submitted = name
    if (!submitted.trim()) return
    setBusy(true)
    try {
      await onAdd(submitted.trim())
      // Keep anything typed while it was saving.
      setName((current) => (current === submitted ? '' : current))
    } catch {
      // Already shown as a toast; keep the text so it can be fixed.
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="flex gap-2">
      <Input
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => e.key === 'Escape' && onCancel?.()}
        placeholder={placeholder}
        aria-label={placeholder}
        autoFocus={autoFocus}
      />
      <Button type="submit" variant="outline" disabled={!name.trim() || busy}>
        <Plus />
        Add
      </Button>
    </form>
  )
}
