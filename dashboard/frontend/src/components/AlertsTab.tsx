import { useStore } from '../store'
import { cn } from '../lib/utils'
import { Bell, AlertTriangle, Info, CheckCircle } from 'lucide-react'

const SEVERITY_STYLE: Record<string, string> = {
  CRITICAL: 'border-l-down text-down bg-down/5',
  HIGH:     'border-l-amber text-amber bg-amber/5',
  MEDIUM:   'border-l-accent text-accent bg-accent/5',
  LOW:      'border-l-border text-text-secondary',
  INFO:     'border-l-border text-text-secondary',
}

const ICONS: Record<string, any> = {
  CRITICAL: AlertTriangle,
  HIGH: AlertTriangle,
  MEDIUM: Info,
  LOW: Info,
  INFO: CheckCircle,
}

export function AlertsTab() {
  const { alerts, apiStatus } = useStore()

  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 text-text-muted">
        <Bell size={40} className="opacity-30" />
        <p className="text-sm">{apiStatus ? `Alerts unavailable: ${apiStatus.status}` : 'No alerts'}</p>
        {apiStatus && <p className="text-xs max-w-md text-center">{apiStatus.message}</p>}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-2 overflow-y-auto h-full">
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
        {alerts.length} Alert{alerts.length !== 1 ? 's' : ''}
      </h3>
      {alerts.map((a: any, i: number) => {
        const sev = a.severity ?? 'INFO'
        const Icon = ICONS[sev] ?? Info
        return (
          <div key={i} className={cn(
            'flex items-start gap-3 p-3 rounded-lg border-l-2 bg-surface-1',
            SEVERITY_STYLE[sev] ?? SEVERITY_STYLE.INFO
          )}>
            <Icon size={14} className="flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium leading-snug">{a.message ?? a.title}</div>
              {a.detail && <div className="text-xs text-text-muted mt-0.5">{a.detail}</div>}
            </div>
            <span className="text-[10px] text-text-muted font-mono flex-shrink-0">
              {a.timestamp_ist ?? a.timestamp ?? ''}
            </span>
          </div>
        )
      })}
    </div>
  )
}
