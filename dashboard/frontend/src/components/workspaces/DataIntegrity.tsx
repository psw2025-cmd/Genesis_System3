import React from 'react';
import { useStore } from '../../store';
import { StatusChip, MetricTile } from './TruthUI';
import { Database, ShieldCheck, Wifi, RefreshCw } from 'lucide-react';
import { formatAgeSec, formatIstStamp, shortSha } from '../../lib/formatLive';
import { brokerIsConnected } from '../../lib/healthTruth';

export const DataIntegrity: React.FC = () => {
  const { health, brokerConnected, wsStatus, lastSync, brokerStatus, state, deployInfo } = useStore();
  const connected = brokerIsConnected(health, brokerConnected, brokerStatus)
  const recon = String(state?.reconciliation?.status || '').toUpperCase()
  const qc = String(state?.qc?.status || '').toUpperCase()
  const latency = health?.broker?.latency_ms ?? brokerStatus?.latency_ms ?? state?.broker?.latency_ms
  const tickAge = state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec
  const blockers = Array.isArray(health?.blockers) ? health.blockers : Array.isArray(health?.live_blockers) ? health.live_blockers : []
  const errors = Array.isArray(health?.errors) ? health.errors : []

  return (
    <div data-testid="data-integrity-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Database size={20} color="var(--accent)" aria-hidden />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Data Integrity</h1>
        </div>
        <StatusChip label="SYNC" value={wsStatus.toUpperCase()} status={wsStatus === 'live' ? 'ok' : 'warn'} />
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 }}>
          <MetricTile label="Reconciliation" value={recon || '—'} tone={recon === 'OK' ? 'ok' : recon ? 'warn' : 'mut'} />
          <MetricTile label="QC" value={qc || '—'} tone={qc === 'PASS' ? 'ok' : qc ? 'warn' : 'mut'} />
          <MetricTile label="Tick age" value={formatAgeSec(tickAge)} />
          <MetricTile label="Deploy SHA" value={shortSha(deployInfo?.git_sha)} sub={String(deployInfo?.service_name || '')} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <ShieldCheck size={16} color="var(--text-sec)" aria-hidden />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Authentication State</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <StatusChip label="DHAN LOGIN" value={connected ? 'AUTHENTICATED' : 'NOT CONNECTED'} status={connected ? 'ok' : 'error'} />
              <StatusChip label="TOKEN" value={brokerStatus?.token_status || (connected ? 'PRESENT' : 'UNKNOWN')} status={connected ? 'ok' : 'warn'} />
              <div style={{ fontSize: '11px', color: 'var(--text-sec)', padding: '8px', background: connected ? 'rgba(0,232,122,0.05)' : 'rgba(255,77,106,0.05)', borderRadius: '4px' }}>
                {connected ? 'Backend reports an active read-only broker session.' : (brokerStatus?.message || brokerStatus?.error || 'Backend reports broker not connected.')}
              </div>
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Wifi size={16} color="var(--text-sec)" aria-hidden />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Broker Connectivity</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <StatusChip label="API PATH" value="CLOUD RUN → DHAN" status="ok" />
              <StatusChip label="WS STATUS" value={wsStatus.toUpperCase()} status={wsStatus === 'live' ? 'ok' : 'warn'} />
              <StatusChip label="LATENCY" value={latency != null ? `${latency}ms` : '—'} status={Number(latency) < 100 ? 'ok' : Number(latency) ? 'warn' : 'mut'} />
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <RefreshCw size={16} color="var(--text-sec)" aria-hidden />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Data Freshness</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <StatusChip label="LAST SYNC" value={formatIstStamp(lastSync)} />
              <StatusChip label="LAST FETCH" value={formatIstStamp(state?.last_fetch_ts_iso)} status={state?.last_fetch_ts_iso ? 'ok' : 'mut'} />
              <StatusChip label="SOURCE" value={state?.data_source || health?.data_source || 'UNKNOWN'} status={state?.data_source || health?.data_source ? 'ok' : 'mut'} />
            </div>
          </section>
        </div>

        <section className="card" style={{ padding: '16px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>API Error Log & Blockers</h2>
          {errors.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {errors.map((err: any, i: number) => (
                <div key={i} style={{ padding: '10px', background: 'rgba(255, 77, 106, 0.05)', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '12px' }}>
                  <span style={{ color: 'var(--down)', fontWeight: 700, marginRight: '8px' }}>[{err.type || 'ERR'}]</span>
                  <span style={{ color: 'var(--text-pri)' }}>{err.message || String(err)}</span>
                </div>
              ))}
            </div>
          ) : blockers.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--amber)', fontSize: 12 }}>
              {blockers.map((b: any, i: number) => <li key={i}>{String(b)}</li>)}
            </ul>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--up)', fontWeight: 600 }}>✓ NO ACTIVE DATA BLOCKERS</div>
          )}
        </section>
      </div>
    </div>
  );
};
