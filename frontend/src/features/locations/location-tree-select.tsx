import { EntityPicker } from '@/components/entity-picker'
import { useLocationTree } from './location-tree'

type Props = {
  value: number | null | undefined
  onChange: (id: number | null) => void
  placeholder?: string
  noneLabel?: string
  /** Locations that can't be picked, e.g. a location and its subtree when moving it. */
  exclude?: Set<number>
  id?: string
  className?: string
}

export function LocationTreeSelect({ placeholder = 'Choose a location', exclude, ...rest }: Props) {
  const { ordered } = useLocationTree()
  const options = ordered
    .filter((node) => !exclude?.has(node.id))
    .map((node) => ({
      id: node.id,
      label: node.name,
      display: node.path,
      hint: node.parentPath,
      depth: node.depth,
    }))
  return (
    <EntityPicker
      options={options}
      placeholder={placeholder}
      searchPlaceholder="Find a location…"
      {...rest}
    />
  )
}
