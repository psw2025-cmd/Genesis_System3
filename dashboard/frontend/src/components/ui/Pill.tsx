import { cn } from '../../lib/utils'
import { StatusDot } from './StatusDot'

type Variant = 'green' | 'red' | 'amber' | 'blue' | 'gray'

const VARS: Record<Variant, string> = {
  green: 'bg-up/10 text-up border-up/20',
  red:   'bg-down/10 text-down border-down/20',
  amber: 'bg-amber/10 text-amber border-amber/20',
  blue:  'bg-accent/15 text-accent border-accent/20',
  gray:  'bg-surface-2 text-text-secondary border-border',
}

const DOT_MAP: Record<Variant, 'live'|'dead'|'warn'|'off'> = {
  green: 'live', red: 'dead', amber: 'warn', blue: 'live', gray: 'off'
}

export function Pill({ label, variant = 'gray', pulse = false, dot = true, small = false }: {
  label: string; variant?: Variant; pulse?: boolean; dot?: boolean; small?: boolean
}) {
  return (
    <span className={cn(
      'pill border',
      VARS[variant],
      small ? 'text-[10px] px-2 py-0.5' : ''
    )}>
      {dot && <StatusDot status={DOT_MAP[variant]} pulse={pulse} />}
      {label}
    </span>
  )
}
