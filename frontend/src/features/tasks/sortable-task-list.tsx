import {
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { ArrowUpToLine, GripVertical } from 'lucide-react'
import { useState } from 'react'
import type { TaskSummary } from '@/api/generated/model'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { TaskRow } from './task-row'

type Props = {
  tasks: TaskSummary[]
  /** The full new order of the open tasks. */
  onReorder: (taskIds: number[]) => void
}

function SortableTask({
  task,
  first,
  onMakeNext,
}: {
  task: TaskSummary
  first: boolean
  onMakeNext: () => void
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id })
  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Translate.toString(transform), transition }}
      className={cn('relative bg-background', isDragging && 'z-10 rounded-md shadow-md')}
    >
      <TaskRow
        task={task}
        handle={
          <button
            ref={setActivatorNodeRef}
            type="button"
            aria-label={`Move ${task.title}`}
            className="-ml-1 mt-0.5 cursor-grab touch-none text-muted-foreground/60 hover:text-foreground active:cursor-grabbing"
            {...attributes}
            {...listeners}
          >
            <GripVertical className="size-4" />
          </button>
        }
        badge={first && <span className="font-medium text-primary">Next step</span>}
        actions={
          !first && (
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={`Make ${task.title} the next step`}
              title="Make next step"
              onClick={onMakeNext}
              className="-my-1 text-muted-foreground"
            >
              <ArrowUpToLine />
            </Button>
          )
        }
      />
    </div>
  )
}

/** Open tasks in order, dragged by their handles. The first is the next step. */
export function SortableTaskList({ tasks, onReorder }: Props) {
  const sensors = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 4 } }),
    // Only the handle starts a drag, so no hold is needed for scrolling to work.
    useSensor(TouchSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )
  // Shows the new order straight away, until the server's order arrives.
  const key = tasks.map((task) => task.id).join(',')
  const [pending, setPending] = useState<{ from: string; ids: number[] } | null>(null)
  const byId = new Map(tasks.map((task) => [task.id, task]))
  const shown =
    pending?.from === key
      ? pending.ids.flatMap((id) => (byId.has(id) ? [byId.get(id)!] : []))
      : tasks

  const reorder = (ids: number[]) => {
    setPending({ from: key, ids })
    onReorder(ids)
  }

  const onDragEnd = ({ active, over }: DragEndEvent) => {
    if (!over || active.id === over.id) return
    const ids = shown.map((task) => task.id)
    reorder(arrayMove(ids, ids.indexOf(Number(active.id)), ids.indexOf(Number(over.id))))
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
      <SortableContext items={shown.map((task) => task.id)} strategy={verticalListSortingStrategy}>
        <div className="-mx-3">
          {shown.map((task, index) => (
            <SortableTask
              key={task.id}
              task={task}
              first={index === 0}
              onMakeNext={() =>
                reorder([task.id, ...shown.filter((t) => t.id !== task.id).map((t) => t.id)])
              }
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  )
}
