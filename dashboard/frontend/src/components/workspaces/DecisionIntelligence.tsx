import React from 'react';
import { Activity, AlertTriangle, Database, Shield, Zap } from 'lucide-react';
import { useStore } from '../../store';
import { MetricTile, StatusChip } from './TruthUI';
import { brokerIsConnected, paperModeActive } from '../../lib/healthTruth';
import { formatAgeSec, formatInr, formatIstStamp, shortSha } from '../../lib/formatLive';

export const DecisionIntelligence: React.FC = () => {
  const {
    health, state, brokerConnected, marketOpen, wsStatus, apiStatus, deployInfo, pnl, paper, setActiveTab,
  } = useStore();
  const dhanOk = brokerIsConnected(health, brokerConnected)
  const apiOk = String(health?.status || apiStatus?.status || '').toLowerCase() === 'ok' || Boolean(health?.mode)
  const predictorRaw = String(health?.predictor?.status || '').toLowerCase()
  const predictorValue = predictorRaw || (paperModeActive(health) ? 'ANALYZER' : 'N/A')
  const predictorTone = predictorRaw === 'ready' || predictorRaw === 'ok' ? 'ok' : 'mut'
  const scannerRaw = String(health?.scanner?.status || '').toLowerCase()
  const scannerValue = scannerRaw || (marketOpen ? 'OFFLINE' : 'AFTER HOURS')
  const scannerTone = scannerRaw === 'active' || scannerRaw === 'ok' ? 'ok' : 'mut'

  const mode = String(health?.mode || state?.mode || 'PAPER').toUpperCase()
  const liveOn = Boolean(state?.live_trading_enabled ?? health?.live_allowed)
  const exposure = state?.risk?.exposure
  const var95 = state?.risk?.var95 ?? state?.risk?.var_95
  const unrealized = state?.pnl?.unrealized ?? pnl?.summary?.total_pnl ?? paper?.pnl?.summary?.total_pnl
  const recon = String(state?.reconciliation?.status || state?.qc?.status || '—').toUpperCase()
  const tickAge = state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec
  const cycle = state?.cycle_count ?? state?.state_version
  const nextOpen = state?.market?.next_open || health?.market?.next_open
  const marketReason = state?.market?.reason || health?.market?.reason
  const brokerMs = health?.broker?.latency_ms ?? state?.broker?.latency_ms
  const signal = String(state?.signals?.status || state?.signals?.reason || 'No signal generated')
  const sha = shortSha(deployInfo?.git_sha)
  const pnlTone = Number(unrealized) < 0 ? 'error' : Number(unrealized) > 0 ? 'ok' : 'mut'
  const runtimeBlockers = Array.isArray(health?.blockers) ? health.blockers : []

  const sectionStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    padding: '16px',
  };

  const gridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '12px',
  };

  return (
    <div data-testid="decision-intel-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 12,
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={20} color="var(--accent)" aria-hidden />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Decision Intelligence</h1>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <StatusChip label="MODE" value={mode} status="warn" />
          <StatusChip label="LIVE" value={liveOn ? 'ON' : 'OFF'} status={liveOn ? 'error' : 'ok'} />
          <StatusChip label="SHA" value={sha} status={sha !== '—' ? 'ok' : 'mut'} />
        </div>
      </header>

      <div style={sectionStyle}>
        {!marketOpen && (
          <div
            data-testid="closed-market-ops-board"
            style={{
              padding: 14,
              borderRadius: 10,
              border: '1px solid rgba(245,165,36,.4)',
              background: 'linear-gradient(135deg, rgba(48,28,8,.55), rgba(8,19,33,.9))',
            }}
          >
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 800, color: 'var(--amber)', marginBottom: 6 }}>
              AFTER-HOURS OPS BOARD
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-sec)', marginBottom: 10, lineHeight: 1.45 }}>
              Market closed — UI stays read-only/poll. QC may show NOT_READY ({String((state?.qc?.reasons || []).join(', ') || 'NO_VERIFIED_CONTRACTS')})
              until live contracts re-verify after next open ({String(nextOpen || '09:15 IST')}).
              Use the tabs below — not only Decision + Chain.
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {[
                ['chain', 'Option Chain'],
                ['options-intel', 'Options Intel'],
                ['broker', 'Broker'],
                ['data-integrity', 'Data Integrity'],
                ['truth', 'Truth Control'],
                ['prediction-audit', 'Prediction Audit'],
                ['performance', 'Performance'],
                ['ml', 'ML Model'],
              ].map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setActiveTab(id)}
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '6px 12px',
                    borderRadius: 6,
                    border: '1px solid var(--border-hi)',
                    background: 'rgba(59,140,255,.14)',
                    color: 'var(--accent-2)',
                    cursor: 'pointer',
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        <h2 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0 }}>
          Live operations
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 }}>
          <MetricTile label="Exposure" value={formatInr(exposure)} sub="Read-only portfolio" />
          <MetricTile label="Unrealized P&L" value={formatInr(unrealized)} tone={pnlTone} sub="Paper / analyzer" />
          <MetricTile label="VaR 95" value={formatInr(var95)} sub="From /api/state" />
          <MetricTile label="Reconciliation" value={recon || '—'} tone={recon === 'OK' || recon === 'PASS' ? 'ok' : 'warn'} />
          <MetricTile label="Tick age" value={formatAgeSec(tickAge)} sub={marketOpen ? 'Market hours' : 'After hours poll'} />
          <MetricTile label="Cycle" value={cycle != null ? String(cycle) : '—'} sub={formatIstStamp(state?.last_fetch_ts_iso)} />
          <MetricTile label="Broker latency" value={brokerMs != null ? `${brokerMs} ms` : '—'} tone={Number(brokerMs) < 200 ? 'ok' : 'warn'} />
          <MetricTile label="Next open" value={String(nextOpen || '—')} sub={String(marketReason || '')} tone={marketOpen ? 'ok' : 'mut'} />
        </div>

        <h2 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', textTransform: 'uppercase', letterSpacing: '0.05em', margin: '8px 0 0' }}>
          System Health & Truth
        </h2>

        <div style={gridStyle}>
          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Shield size={16} color="var(--text-sec)" aria-hidden />
              <span style={{ fontWeight: 600 }}>Truth Control</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <StatusChip label="BROKER" value={dhanOk ? 'CONNECTED' : 'DISCONNECTED'} status={dhanOk ? 'ok' : 'error'} />
              <StatusChip label="WS" value={wsStatus.toUpperCase()} status={wsStatus === 'live' ? 'ok' : wsStatus === 'error' ? 'error' : 'warn'} />
              <StatusChip label="MARKET" value={marketOpen ? 'OPEN' : 'CLOSED'} status={marketOpen ? 'ok' : 'mut'} />
            </div>
          </div>

          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Activity size={16} color="var(--text-sec)" aria-hidden />
              <span style={{ fontWeight: 600 }}>Service Availability</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <StatusChip label="API" value={apiOk ? 'OK' : (apiStatus?.status || 'UNKNOWN')} status={apiOk ? 'ok' : 'warn'} />
              <StatusChip label="SCANNER" value={scannerValue.toUpperCase()} status={scannerTone} />
              <StatusChip label="PREDICTOR" value={predictorValue.toUpperCase()} status={predictorTone} />
            </div>
          </div>

          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Database size={16} color="var(--text-sec)" aria-hidden />
              <span style={{ fontWeight: 600 }}>Data Sources</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <StatusChip label="DHAN" value={dhanOk ? 'AUTH OK' : 'NO AUTH'} status={dhanOk ? 'ok' : 'error'} />
              <StatusChip label="SOURCE" value={state?.data_source || health?.data_source || 'UNKNOWN'} status={state?.data_source || health?.data_source ? 'ok' : 'mut'} />
              <StatusChip label="DEPLOY" value={String(deployInfo?.deploy_target || 'gcp-cloud-run')} status="ok" />
            </div>
          </div>

          <div className="card" style={{ padding: '16px', background: runtimeBlockers.length ? 'rgba(255, 77, 106, 0.03)' : 'rgba(16,185,129,.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <AlertTriangle size={16} color={runtimeBlockers.length ? 'var(--down)' : 'var(--up)'} aria-hidden />
              <span style={{ fontWeight: 600, color: runtimeBlockers.length ? 'var(--down)' : 'var(--up)' }}>Runtime Connectivity Blockers</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-sec)' }}>
              {runtimeBlockers.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: '16px' }}>
                  {runtimeBlockers.map((b: any, i: number) => <li key={i}>{b}</li>)}
                </ul>
              ) : (
                <div>
                  <div style={{ color: 'var(--up)', fontWeight: 600 }}>✓ NO RUNTIME CONNECTIVITY BLOCKERS</div>
                  <div style={{ color: 'var(--text-mut)', marginTop: 6, lineHeight: 1.45 }}>This does not mean model maturity, E2E evidence, human approval, or live-money gates are complete. See E2E Proof and Live Gate for those independent blockers.</div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: '16px', marginTop: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', marginBottom: '8px' }}>LIVE DECISION BRIEF</div>
          <div style={{ fontSize: '13px', lineHeight: 1.5, color: 'var(--text-pri)', marginBottom: '12px' }}>
            Operating in <strong>{mode}</strong> with <strong>LIVE {liveOn ? 'ON' : 'OFF'}</strong>.
            Signal: {signal}. Last fetch {formatIstStamp(state?.last_fetch_ts_iso)}.
            Automated order placement remains inhibited by safety gates.
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button type="button" className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('truth')}>TRUTH CONTROL</button>
            <button type="button" className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('options-intel')}>OPTIONS INTEL</button>
            <button type="button" className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('risk-scenarios')}>RISK & SCENARIOS</button>
            <button type="button" className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('data-integrity')}>DATA INTEGRITY</button>
          </div>
        </div>
      </div>
    </div>
  );
};
