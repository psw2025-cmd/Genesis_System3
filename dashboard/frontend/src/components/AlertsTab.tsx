import { useStore } from '../store'
import { splitAlertStream } from '../lib/alertTruth'
import { cn } from '../lib/utils'
import { Bell, AlertTriangle, Info, CheckCircle, Activity, Shield } from 'lucide-react'

const SEVERITY_STYLE: Record<string, string> = {
  CRITICAL: 'border-l-down text-down bg-down/5',
  HIGH: 'border-l-amber text-amber bg-amber/5',
  MEDIUM: 'border-l-accent text-accent bg-accent/5',
  LOW: 'border-l-border text-text-secondary',
  INFO: 'border-l-border text-text-secondary',
}

const ICONS: Record<string, any> = {
  CRITICAL: AlertTriangle,
  HIGH: AlertTriangle,
  MEDIUM: Info,
  LOW: Info,
  INFO: CheckCircle,
}

export function AlertsTab() {
  const { alerts, alertFeedStatus, marketOpen, brokerConnected, wsStatus } = useStore()
  const { liveReadinessInfo, activeAlerts } = splitAlertStream(alerts)
  const feedReady = alertFeedStatus.state === 'ready'
  const counts = activeAlerts.reduce<Record<string, number>>((acc, alert: any) => {
    const severity = String(alert?.severity ?? 'INFO').toUpperCase()
    acc[severity] = (acc[severity] || 0) + 1
    return acc
  }, {})

  const feedLabel = feedReady
    ? (activeAlerts.length ? `${activeAlerts.length} ACTIVE` : 'NO ACTIVE ALERTS')
    : alertFeedStatus.state === 'loading' ? 'FEED LOADING' : 'FEED DEGRADED'
  const feedTone = feedReady
    ? (activeAlerts.length ? 'var(--amber)' : 'var(--up)')
    : alertFeedStatus.state === 'loading' ? 'var(--accent)' : 'var(--down)'
  const feedBorder = feedReady
    ? (activeAlerts.length ? 'rgba(245,165,36,.25)' : 'rgba(24,215,130,.22)')
    : alertFeedStatus.state === 'loading' ? 'rgba(59,140,255,.28)' : 'rgba(255,73,100,.28)'

  const metrics = [
    ['Critical', String(counts.CRITICAL || 0), counts.CRITICAL ? 'var(--down)' : 'var(--text-pri)'],
    ['High', String(counts.HIGH || 0), counts.HIGH ? 'var(--amber)' : 'var(--text-pri)'],
    ['Medium', String(counts.MEDIUM || 0), counts.MEDIUM ? 'var(--accent)' : 'var(--text-pri)'],
    ['Market', marketOpen ? 'OPEN' : 'CLOSED', marketOpen ? 'var(--up)' : 'var(--amber)'],
    ['Broker', brokerConnected ? 'CONNECTED' : 'WAITING', brokerConnected ? 'var(--up)' : 'var(--amber)'],
    ['WebSocket transport', wsStatus === 'live' ? 'TRANSPORT LIVE' : wsStatus.toUpperCase(), wsStatus === 'live' ? 'var(--up)' : 'var(--amber)'],
  ]

  return (
    <div className="workspace-shell alerts-workspace">
      <div className="card alerts-header-card">
        <div className="alerts-header-row">
          <div className="alerts-heading-group">
            <div className="alerts-heading-icon"><Bell size={17} /></div>
            <div className="alerts-heading-copy">
              <div className="workspace-title">Alerts & Activity Intelligence</div>
              <div className="alerts-subtitle">System, broker, data-quality and model notifications</div>
            </div>
          </div>
          <span className="pill" style={{ color: feedTone, border: `1px solid ${feedBorder}`, background: `${feedTone}0d` }}>
            {feedLabel}
          </span>
        </div>
      </div>

      <div className="workspace-grid alerts-metrics-grid">
        {metrics.map(([label, value, color]) => (
          <div className="metric-card alerts-metric-card" key={label}>
            <div className="metric-label">{label}</div>
            <div className="metric-value alerts-metric-value" style={{ color }}>{value}</div>
          </div>
        ))}
      </div>

      <div className="workspace-grid alerts-content-grid">
        <div className="card alerts-stream-card">
          <div className="alerts-stream-header">
            <div className="panel-title">Live Alert Stream</div>
            <span>Newest evidence first</span>
          </div>

          {activeAlerts.length === 0 ? (
            <div className="alerts-empty-state">
              <div className="alerts-empty-copy">
                <div className={cn('alerts-empty-icon', !feedReady && 'alerts-empty-icon-degraded')}>
                  {feedReady ? <CheckCircle size={25} /> : <AlertTriangle size={25} />}
                </div>
                <div className="alerts-empty-title">{feedReady ? 'No active alerts' : 'Alert feed unavailable'}</div>
                <div className="alerts-empty-detail">
                  {feedReady
                    ? 'The operational alert feed was read successfully and is clear. Live-readiness information is tracked separately and cannot change trading authority.'
                    : alertFeedStatus.state === 'loading'
                      ? 'Waiting for the first successful alert-feed read. An empty list is not treated as proof that there are no alerts.'
                      : (alertFeedStatus.message || 'The latest alert-feed request failed. No-clear state is asserted until the feed recovers.')}
                </div>
              </div>
            </div>
          ) : (
            <div className="alerts-list">
              {!feedReady && (
                <div className="alerts-degraded-banner" role="status">
                  Showing last-known alerts. {alertFeedStatus.message || 'The live alert feed is temporarily unavailable.'}
                </div>
              )}
              {activeAlerts.map((a: any, i: number) => {
                const sev = String(a.severity ?? 'INFO').toUpperCase()
                const Icon = ICONS[sev] ?? Info
                return (
                  <div key={i} className={cn('alerts-list-item flex items-start gap-3 p-3 rounded-lg border-l-2 bg-surface-1', SEVERITY_STYLE[sev] ?? SEVERITY_STYLE.INFO)}>
                    <Icon size={14} className="flex-shrink-0 mt-0.5" />
                    <div className="alerts-list-copy flex-1 min-w-0">
                      <div className="alerts-message text-sm font-medium leading-snug">{a.message ?? a.title ?? 'Alert'}</div>
                      {a.detail && <div className="alerts-detail text-xs text-text-muted mt-0.5">{a.detail}</div>}
                    </div>
                    <span className="alerts-timestamp text-[10px] text-text-muted font-mono">{a.timestamp_ist ?? a.timestamp ?? ''}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="alerts-side-column">
          <div className="card alerts-side-card">
            <div className="alerts-panel-heading"><Activity size={14} color="var(--accent)" /><div className="panel-title">Monitoring Channels</div></div>
            {['Market & chain data', 'Broker connectivity', 'Model / ML evidence', 'Risk & truth gates', 'System runtime'].map((label) => (
              <div className="alerts-monitor-row" key={label}>
                <span>{label}</span><strong>MONITORED</strong>
              </div>
            ))}
          </div>
          <div className="card alerts-side-card">
            <div className="alerts-panel-heading"><Shield size={14} color="var(--up)" /><div className="panel-title">Live Readiness</div></div>
            <div className="alerts-authority-value">BLOCKED BY DESIGN</div>
            <div className="alerts-authority-copy">
              {liveReadinessInfo.length
                ? `${liveReadinessInfo.length} informational live-readiness record${liveReadinessInfo.length === 1 ? '' : 's'} tracked separately; live approval is not required for PAPER/ANALYZER operation.`
                : 'No live-readiness record is being promoted into the active operational alert count; live approval is not required for PAPER/ANALYZER operation.'}
            </div>
          </div>
          <div className="card alerts-side-card">
            <div className="alerts-panel-heading"><Shield size={14} color="var(--up)" /><div className="panel-title">Authority</div></div>
            <div className="alerts-authority-value">ANALYZER / PAPER · LIVE OFF</div>
            <div className="alerts-authority-copy">Alert handling is observational. WebSocket transport health is separate from broker/API authority. This tab does not expose order execution.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
