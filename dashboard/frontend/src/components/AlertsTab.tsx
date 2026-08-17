import { useStore } from '../store'
import { cn } from '../lib/utils'
import { Bell, AlertTriangle, Info, CheckCircle, Activity, Shield } from 'lucide-react'

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

const isLiveReadinessInfo = (alert: any) => {
  const type = String(alert?.type ?? alert?.category ?? alert?.code ?? '').toUpperCase()
  const severity = String(alert?.severity ?? 'INFO').toUpperCase()
  return type === 'LIVE_GATE' && severity === 'INFO'
}

export function AlertsTab() {
  const { alerts, apiStatus, marketOpen, brokerConnected, wsStatus } = useStore()
  const authIssue = Boolean(apiStatus && /auth|401|403/i.test(String(apiStatus.status || apiStatus.message || '')))
  const liveReadinessInfo = alerts.filter(isLiveReadinessInfo)
  const activeAlerts = alerts.filter((alert: any) => !isLiveReadinessInfo(alert))
  const counts = activeAlerts.reduce<Record<string, number>>((acc, alert: any) => {
    const severity = String(alert?.severity ?? 'INFO').toUpperCase()
    acc[severity] = (acc[severity] || 0) + 1
    return acc
  }, {})

  return (
    <div className="workspace-shell">
      <div className="card" style={{ padding: 12, marginBottom: 9 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
            <div style={{ width: 34, height: 34, display: 'grid', placeItems: 'center', borderRadius: 9, color: 'var(--accent)', background: 'rgba(59,140,255,.10)', border: '1px solid rgba(59,140,255,.28)' }}><Bell size={17} /></div>
            <div>
              <div className="workspace-title">Alerts & Activity Intelligence</div>
              <div style={{ marginTop: 3, color: 'var(--text-mut)', fontSize: '.59rem' }}>System, broker, data-quality and model notifications</div>
            </div>
          </div>
          <span className="pill" style={{ color: activeAlerts.length ? 'var(--amber)' : 'var(--up)', border: `1px solid ${activeAlerts.length ? 'rgba(245,165,36,.25)' : 'rgba(24,215,130,.22)'}`, background: activeAlerts.length ? 'rgba(245,165,36,.06)' : 'rgba(24,215,130,.05)' }}>
            {activeAlerts.length ? `${activeAlerts.length} ACTIVE` : 'NO ACTIVE ALERTS'}
          </span>
        </div>
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: 'repeat(6, minmax(0, 1fr))', marginBottom: 9 }}>
        {[
          ['Critical', String(counts.CRITICAL || 0), counts.CRITICAL ? 'var(--down)' : 'var(--text-pri)'],
          ['High', String(counts.HIGH || 0), counts.HIGH ? 'var(--amber)' : 'var(--text-pri)'],
          ['Medium', String(counts.MEDIUM || 0), counts.MEDIUM ? 'var(--accent)' : 'var(--text-pri)'],
          ['Market', marketOpen ? 'OPEN' : 'CLOSED', marketOpen ? 'var(--up)' : 'var(--amber)'],
          ['Broker', brokerConnected ? 'CONNECTED' : 'WAITING', brokerConnected ? 'var(--up)' : 'var(--amber)'],
          ['WebSocket', wsStatus.toUpperCase(), wsStatus === 'live' ? 'var(--up)' : 'var(--amber)'],
        ].map(([label, value, color]) => (
          <div className="metric-card" key={label}>
            <div className="metric-label">{label}</div>
            <div className="metric-value" style={{ color, fontSize: '1rem' }}>{value}</div>
          </div>
        ))}
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: 'minmax(0, 2.5fr) minmax(260px, 1fr)' }}>
        <div className="card" style={{ overflow: 'hidden', minHeight: 430 }}>
          <div style={{ padding: '11px 13px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="panel-title">Live Alert Stream</div>
            <span style={{ color: 'var(--text-mut)', fontSize: '.55rem' }}>Newest evidence first</span>
          </div>

          {activeAlerts.length === 0 ? (
            <div style={{ minHeight: 360, display: 'grid', placeItems: 'center', padding: 24 }}>
              <div style={{ textAlign: 'center', maxWidth: 520 }}>
                <div style={{ width: 54, height: 54, borderRadius: 14, display: 'grid', placeItems: 'center', margin: '0 auto', color: 'var(--up)', border: '1px solid rgba(24,215,130,.24)', background: 'rgba(24,215,130,.06)' }}><CheckCircle size={25} /></div>
                <div style={{ marginTop: 14, color: 'var(--text-pri)', fontWeight: 800, fontSize: '.84rem' }}>No active alerts</div>
                <div style={{ marginTop: 7, color: 'var(--text-mut)', fontSize: '.65rem', lineHeight: 1.65 }}>
                  {authIssue ? (apiStatus?.message || apiStatus?.status) : 'The operational alert stream is clear. Live-readiness information is tracked separately and cannot change trading authority.'}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: 10, display: 'grid', gap: 7 }}>
              {activeAlerts.map((a: any, i: number) => {
                const sev = String(a.severity ?? 'INFO').toUpperCase()
                const Icon = ICONS[sev] ?? Info
                return (
                  <div key={i} className={cn('flex items-start gap-3 p-3 rounded-lg border-l-2 bg-surface-1', SEVERITY_STYLE[sev] ?? SEVERITY_STYLE.INFO)} style={{ border: '1px solid var(--border)', borderLeftWidth: 3 }}>
                    <Icon size={14} className="flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium leading-snug">{a.message ?? a.title ?? 'Alert'}</div>
                      {a.detail && <div className="text-xs text-text-muted mt-0.5">{a.detail}</div>}
                    </div>
                    <span className="text-[10px] text-text-muted font-mono flex-shrink-0">{a.timestamp_ist ?? a.timestamp ?? ''}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div style={{ display: 'grid', gap: 9, alignContent: 'start' }}>
          <div className="card" style={{ padding: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}><Activity size={14} color="var(--accent)" /><div className="panel-title">Monitoring Channels</div></div>
            {['Market & chain data', 'Broker connectivity', 'Model / ML evidence', 'Risk & truth gates', 'System runtime'].map((label) => (
              <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: '.62rem' }}>
                <span style={{ color: 'var(--text-sec)' }}>{label}</span><span style={{ color: 'var(--up)', fontWeight: 800 }}>MONITORED</span>
              </div>
            ))}
          </div>
          <div className="card" style={{ padding: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}><Shield size={14} color="var(--up)" /><div className="panel-title">Live Readiness</div></div>
            <div style={{ marginTop: 9, color: 'var(--up)', fontWeight: 800, fontSize: '.66rem' }}>BLOCKED BY DESIGN</div>
            <div style={{ marginTop: 6, color: 'var(--text-mut)', fontSize: '.59rem', lineHeight: 1.6 }}>
              {liveReadinessInfo.length
                ? `${liveReadinessInfo.length} informational live-readiness record${liveReadinessInfo.length === 1 ? '' : 's'} tracked separately; live approval is not required for PAPER/ANALYZER operation.`
                : 'No live-readiness record is being promoted into the active operational alert count; live approval is not required for PAPER/ANALYZER operation.'}
            </div>
          </div>
          <div className="card" style={{ padding: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}><Shield size={14} color="var(--up)" /><div className="panel-title">Authority</div></div>
            <div style={{ marginTop: 9, color: 'var(--up)', fontWeight: 800, fontSize: '.66rem' }}>ANALYZER / PAPER · LIVE OFF</div>
            <div style={{ marginTop: 6, color: 'var(--text-mut)', fontSize: '.59rem', lineHeight: 1.6 }}>Alert handling is observational. This tab does not expose order execution.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
