import { useMemo } from 'react'
import { useListLocations } from '@/api/generated/locations/locations'
import type { LocationOut } from '@/api/generated/model'

export type LocationNode = LocationOut & {
  depth: number
  /** e.g. "Workshop › Shelf A". */
  path: string
  /** The path of its parent, "" for a zone. */
  parentPath: string
  children: LocationNode[]
}

/** Locations arrive flat and sorted by name; this nests them, keeping that order. */
export function buildLocationTree(locations: LocationOut[]) {
  const byId = new Map<number, LocationNode>()
  for (const location of locations) {
    byId.set(location.id, { ...location, depth: 0, path: '', parentPath: '', children: [] })
  }
  const roots: LocationNode[] = []
  for (const node of byId.values()) {
    const parent = node.parent_id == null ? undefined : byId.get(node.parent_id)
    ;(parent ? parent.children : roots).push(node)
  }
  // Depth-first, so a flat list reads as an indented tree.
  const ordered: LocationNode[] = []
  const walk = (nodes: LocationNode[], depth: number, parentPath: string) => {
    for (const node of nodes) {
      node.depth = depth
      node.parentPath = parentPath
      node.path = parentPath ? `${parentPath} › ${node.name}` : node.name
      ordered.push(node)
      walk(node.children, depth + 1, node.path)
    }
  }
  walk(roots, 0, '')
  return { roots, byId, ordered }
}

export function subtreeIds(node: LocationNode): Set<number> {
  const ids = new Set<number>()
  const walk = (n: LocationNode) => {
    ids.add(n.id)
    n.children.forEach(walk)
  }
  walk(node)
  return ids
}

export function useLocationTree() {
  const { data, isPending } = useListLocations()
  const tree = useMemo(() => buildLocationTree(data ?? []), [data])
  return { ...tree, isPending }
}
