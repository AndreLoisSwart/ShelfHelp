import { Link } from 'react-router'
import type { ProjectSummary } from '@/api/generated/model'
import { StatusBadge } from '@/components/status-badge'
import { TagChips } from '@/components/tag-chips'
import { timeAgo } from '@/lib/format'
import { cn } from '@/lib/utils'

type Props = {
  project: ProjectSummary
  /** Off on the board, where the column already says it. */
  showStatus?: boolean
  className?: string
}

export function ProjectCard({ project, showStatus = true, className }: Props) {
  return (
    <Link
      to={`/projects/${project.id}`}
      className={cn(
        'block rounded-lg border bg-card p-3 text-card-foreground transition-colors hover:border-ring/60',
        className,
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="leading-snug font-medium">{project.name}</h3>
        {showStatus && <StatusBadge status={project.status} />}
      </div>
      {project.next_step ? (
        <p className="mt-1 text-sm">
          <span className="text-muted-foreground">Next: </span>
          {project.next_step}
        </p>
      ) : (
        <p className="mt-1 text-sm text-muted-foreground italic">No next step</p>
      )}
      <div className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
        <span>Touched {timeAgo(project.last_touched_at)}</span>
        <TagChips tags={project.tags} />
      </div>
    </Link>
  )
}
