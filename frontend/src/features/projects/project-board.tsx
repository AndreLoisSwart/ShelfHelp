import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import { useRef, useState } from 'react'
import type { ProjectStatus, ProjectSummary } from '@/api/generated/model'
import { PROJECT_STATUS_LABELS } from '@/lib/statuses'
import { cn } from '@/lib/utils'
import { ProjectCard } from './project-card'

type Props = {
  projects: ProjectSummary[]
  statuses: ProjectStatus[]
  onMove: (projectId: number, status: ProjectStatus) => void
}

function DraggableCard({ project }: { project: ProjectSummary }) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({ id: project.id })
  return (
    <div ref={setNodeRef} {...attributes} {...listeners} className={cn(isDragging && 'opacity-40')}>
      <ProjectCard project={project} showStatus={false} />
    </div>
  )
}

function Column({ status, projects }: { status: ProjectStatus; projects: ProjectSummary[] }) {
  const { setNodeRef, isOver } = useDroppable({ id: status })
  return (
    <section
      ref={setNodeRef}
      aria-label={PROJECT_STATUS_LABELS[status]}
      className={cn(
        'flex min-w-56 flex-1 basis-0 snap-start flex-col gap-2 rounded-lg bg-muted/50 p-2 transition-shadow',
        isOver && 'ring-2 ring-ring/50',
      )}
    >
      <h2 className="flex items-center justify-between px-1 pt-1 text-sm font-medium">
        {PROJECT_STATUS_LABELS[status]}
        <span className="text-xs font-normal text-muted-foreground">{projects.length}</span>
      </h2>
      {projects.map((project) => (
        <DraggableCard key={project.id} project={project} />
      ))}
      {projects.length === 0 && (
        <p className="px-1 py-6 text-center text-xs text-muted-foreground">Drop a project here</p>
      )}
    </section>
  )
}

/** A column per status. Dragging a card to another column changes its status. */
export function ProjectBoard({ projects, statuses, onMove }: Props) {
  const [activeId, setActiveId] = useState<number | null>(null)
  const [animateDrop, setAnimateDrop] = useState(true)
  // A drag that ends over the card's own link would otherwise also open the project.
  const justDragged = useRef(false)
  const sensors = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 6 } }),
    // Press and hold on touch, so a swipe still scrolls the board.
    useSensor(TouchSensor, { activationConstraint: { delay: 250, tolerance: 8 } }),
    useSensor(KeyboardSensor),
  )
  const active = projects.find((project) => project.id === activeId)

  const onDragEnd = ({ active, over }: DragEndEvent) => {
    setTimeout(() => (justDragged.current = false))
    const project = projects.find((p) => p.id === active.id)
    const status = over?.id as ProjectStatus | undefined
    const target = project && status && project.status !== status ? status : null
    // Set with the drag ending, so the overlay reads it as it drops.
    setAnimateDrop(target === null)
    setActiveId(null)
    if (project && target) onMove(project.id, target)
  }

  return (
    <DndContext
      sensors={sensors}
      onDragStart={({ active }) => {
        justDragged.current = true
        setActiveId(Number(active.id))
      }}
      onDragEnd={onDragEnd}
      onDragCancel={() => {
        setAnimateDrop(true)
        setActiveId(null)
      }}
    >
      <div
        className="-mx-4 flex snap-x scroll-px-4 gap-2 overflow-x-auto px-4 pb-2 md:mx-0 md:scroll-px-0 md:px-0"
        onClickCapture={(e) => {
          if (justDragged.current) {
            e.preventDefault()
            e.stopPropagation()
          }
        }}
      >
        {statuses.map((status) => (
          <Column
            key={status}
            status={status}
            projects={projects.filter((project) => project.status === status)}
          />
        ))}
      </div>
      {/* The default animation glides back to the card's old spot, which is wrong once the
          card has moved column: it would fly back, then jump. Only animate a drag that's undone. */}
      <DragOverlay dropAnimation={animateDrop ? undefined : null}>
        {active && (
          <ProjectCard project={active} showStatus={false} className="rotate-2 shadow-lg" />
        )}
      </DragOverlay>
    </DndContext>
  )
}
