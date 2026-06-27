import { cn } from '../../lib/utils'

type Status = 'live' | 'warn' | 'dead' | 'off'

const COLORS: Record<Status, string> = {
  live: 'bg-up',
  warn: 'bg-amber',
  dead: 'bg-down',
  off:  'bg-text-muted',
}

export function StatusDot({ status = 'off', pulse = false }: {
  status?: Status; pulse?: boolean
}) {
  return (
    <span className={cn(
      'inline-block w-2 h-2 rounded-full flex-shrink-0',
      COLORS[status],
      pulse && status === 'live' && 'animate-pulse-dot'
    )} />
  )
}
