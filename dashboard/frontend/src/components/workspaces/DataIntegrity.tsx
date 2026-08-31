import React from 'react'
import { useStore } from '../../store'
import { StatusChip, MetricTile } from './TruthUI'
import { Database, ShieldCheck, Wifi, RefreshCw } from 'lucide-react'
import { formatAgeSec, formatIstStamp, shortSha } from '../../lib/formatLive'
import { brokerIsConnected } from '../../lib/healthTruth'
import { resolveFeedQuality } from '../../lib/feedQuality'
import { SystemHealthDiagnostics } from '../SystemHealthDiagnostics'
import { SystemProgressPanel } from '../SystemProgressPanel'

const REQUIRED_OPTION_CHAINS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'] as const

function verifiedDhanContracts(chain: Record<string, any> | null | undefined): number {
  return REQUIRED_OPTION_CHAINS.reduce((total, symbol) => {
    const payload = chain?.[symbol]
    if (!payload || typeof payload !== 'object') return total

    const source = String(payload.data_source || payload.source || '').toLowerCase()
    const priority = String(payload.source_priority || '').toLowerCase()
    const status = String(payload.status || '').toUpperCase()
    const dhanBacked = source.includes('dhan') || priority.startsWith('dhan') || priority.includes('worker_push')
    const staleUnverified = payload.stale === true
      && !/MARKET_CLOSED|SNAPSHOT/.test(status)
      && payload.snapshot !== true
      && payload.live !== false
    const count = Number(
      payload.total_contracts
      ?? payload.contract_count
      ?? (Array.isArray(payload.contracts) ? payload.contracts.length : 0),
    )

    return dhanBacked && !staleUnverified && Number.isFinite(count) && count > 0
      ? total + count
      : total
  }, 0)
}

export const DataIntegrity: React.FC = () => {
  const { health, brokerConnected, wsStatus, lastSync, brokerStatus, state, deployInfo, marketOpen, chain } = useStore()
  const connected = brokerIsConnected(health, brokerConnected, brokerStatus)
  const recon = String(state?.reconciliation?.status || '').toUpperCase()
  const qc = String(state?.qc?.status || '').toUpperCase()
  const latency = health?.broker?.latency_ms ?? brokerStatus?.latency_ms ?? state?.broker?.latency_ms
  const tickAge = state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec
  const explicitBlockers = Array.isArray(health?.blockers)
    ? health.blockers
    : Array.isArray(health?.live_blockers)
      ? health.live_blockers
      : []
  const brokerError = String(brokerStatus?.error || state?.broker?.error || '').trim()
  const contractsRaw = state?.qc?.contracts_total
  const qcContractsTotal = Number(contractsRaw ?? 0)
  const chainContractsTotal = verifiedDhanContracts(chain)
  const verifiedContractsTotal = Number.isFinite(qcContractsTotal) && qcContractsTotal > 0
    ? qcContractsTotal
    : chainContractsTotal
  const derivedBlockers: string[] = []
  if (!connected && (Boolean(marketOpen) || Boolean(brokerError))) {
    derivedBlockers.push(brokerError ? `Broker not connected: ${brokerError}` : 'Broker not connected during market hours')
  }
  if (qc && qc !== 'PASS') {
    derivedBlockers.push(`QC ${qc}`)
  }
  if (!Number.isFinite(verifiedContractsTotal) || verifiedContractsTotal <= 0) {
    derivedBlockers.push('No verified option contracts')
  }
  const blockers = Array.from(new Set([...explicitBlockers.map((b: any) => String(b)), ...derivedBlockers]))
  const errors = Array.isArray(health?.errors) ? health.errors : []
  const feed = resolveFeedQuality({
    marketOpen,
    wsStatus,
    tickAgeSec: tickAge,
    dataSource: state?.data_source || health?.data_source,
    brokerConnected: connected,
  })

  return (
    <div data-testid="data-integrity-root" className="workspace-page">
      <header className="workspace-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Database size={18} color="var(--accent)" aria-hidden />
          <div>
            <h1 className="workspace-h1">Data integrity</h1>
            <p className="workspace-lead">Freshness, broker auth, and engineering diagnostics</p>
          </div>
        </div>
        <span className={`feed-badge feed-badge-${feed.tone}`}>{feed.label}</span>
      </header>

      <div className="workspace-body">
        <SystemHealthDiagnostics variant="panel" />
        <SystemProgressPanel />

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 }}>
          <MetricTile label="Reconciliation" value={recon || '—'} tone={recon === 'OK' ? 'ok' : recon ? 'warn' : 'mut'} />
          <MetricTile label="QC" value={qc || '—'} tone={qc === 'PASS' ? 'ok' : qc ? 'warn' : 'mut'} />
          <MetricTile label="Tick age" value={formatAgeSec(tickAge)} />
          <MetricTile label="Deploy SHA" value={shortSha(deployInfo?.git_sha)} sub={String(deployInfo?.service_name || '')} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          <section className="elevated-panel" style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <ShieldCheck size={16} color="var(--text-sec)" aria-hidden />
              <h2 className="section-title" style={{ margin: 0 }}>Authentication</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <StatusChip label="Dhan login" value={connected ? 'Authenticated' : 'Not connected'} status={connected ? 'ok' : 'error'} />
              <StatusChip
                label="Token"
                value={
                  connected
                    ? (brokerStatus?.token_proof?.secret_version
                        ? `SM v${brokerStatus.token_proof.secret_version}`
                        : (brokerStatus?.token_status || 'Present'))
                    : (brokerStatus?.error || brokerStatus?.token_status || 'Unknown')
                }
                status={connected ? 'ok' : 'warn'}
              />
              <div style={{ fontSize: 12, color: 'var(--text-sec)', padding: 10, background: 'var(--surface-2)', borderRadius: 8 }}>
                {connected
                  ? `Backend reports an active read-only broker session${
                      brokerStatus?.token_proof?.hours_remaining != null
                        ? ` · ~${Number(brokerStatus.token_proof.hours_remaining).toFixed(1)}h nominal JWT left`
                        : ''
                    }.`
                  : (
                    <>
                      {brokerStatus?.message || brokerStatus?.error || 'Backend reports broker not connected.'}
                      {String(brokerStatus?.error || '').includes('TOKEN_EXPIRED') && brokerStatus?.token_proof?.expired === false
                        ? ' (label is auth-reject; JWT clock may still be valid — check DH-906 / remint.)'
                        : ''}
                    </>
                  )}
              </div>
            </div>
          </section>

          <section className="elevated-panel" style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <Wifi size={16} color="var(--text-sec)" aria-hidden />
              <h2 className="section-title" style={{ margin: 0 }}>Connectivity</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <StatusChip label="API path" value="Cloud Run → Dhan" status="ok" />
              <StatusChip label="WebSocket" value={wsStatus} status={wsStatus === 'live' ? 'ok' : 'warn'} />
              <StatusChip label="Latency" value={latency != null ? `${latency} ms` : '—'} status={Number(latency) < 100 ? 'ok' : Number(latency) ? 'warn' : 'mut'} />
            </div>
          </section>

          <section className="elevated-panel" style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <RefreshCw size={16} color="var(--text-sec)" aria-hidden />
              <h2 className="section-title" style={{ margin: 0 }}>Freshness</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <StatusChip label="Last sync" value={formatIstStamp(lastSync)} />
              <StatusChip label="Last fetch" value={formatIstStamp(state?.last_fetch_ts_iso)} status={state?.last_fetch_ts_iso ? 'ok' : 'mut'} />
              <StatusChip label="Source" value={state?.data_source || health?.data_source || 'Unknown'} status={state?.data_source || health?.data_source ? 'ok' : 'mut'} />
            </div>
          </section>
        </div>

        <section className="elevated-panel" style={{ padding: 16 }}>
          <h2 className="section-title">Errors and blockers</h2>
          {errors.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {errors.map((err: any, i: number) => (
                <div key={i} style={{ padding: 10, background: 'rgba(255, 77, 106, 0.05)', borderRadius: 8, fontSize: 12 }}>
                  <span style={{ color: 'var(--down)', fontWeight: 700, marginRight: 8 }}>[{err.type || 'ERR'}]</span>
                  <span style={{ color: 'var(--text-pri)' }}>{err.message || String(err)}</span>
                </div>
              ))}
            </div>
          ) : blockers.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--amber)', fontSize: 12 }}>
              {blockers.map((b: any, i: number) => <li key={i}>{String(b)}</li>)}
            </ul>
          ) : (
            <div style={{ textAlign: 'center', padding: 16, color: 'var(--up)', fontWeight: 600 }}>No active data blockers</div>
          )}
        </section>
      </div>
    </div>
  )
}
