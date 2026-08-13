import React from 'react';
import { Search } from 'lucide-react';
import { useStore } from '../../store';
import { MetricTile, PENDINGState, StatusChip } from './TruthUI';
import { formatIstStamp } from '../../lib/formatLive';

export const PredictionAudit: React.FC = () => {
  const { autoGates, state, health, lastSync } = useStore()
  const gates: any[] = Array.isArray(autoGates?.proof_gates)
    ? autoGates.proof_gates
    : Object.entries(autoGates?.gates || {}).map(([gate_id, gate]: [string, any]) => ({
        gate_id,
        label: gate_id,
        ...(typeof gate === 'object' ? gate : { status: gate }),
      }))
  const signal = state?.signals || {}
  const passCount = gates.filter((g) => g?.pass === true || String(g?.status).toUpperCase() === 'PASS').length

  return (
    <div data-testid="prediction-audit-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Search size={20} color="var(--accent)" aria-hidden />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Prediction Audit Ledger</h1>
        </div>
        <StatusChip label="GATES" value={`${passCount}/${gates.length || 0} PASS`} status={gates.length ? 'ok' : 'mut'} />
      </header>
      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 }}>
          <MetricTile label="Last signal" value={String(signal.status || 'NO_TRADE')} sub={String(signal.reason || 'No signal generated')} />
          <MetricTile label="Confidence" value={signal.confidence != null ? String(signal.confidence) : '—'} />
          <MetricTile label="Cycle" value={state?.cycle_count != null ? String(state.cycle_count) : '—'} sub={formatIstStamp(state?.last_cycle_ts_iso || lastSync)} />
          <MetricTile label="Mode" value={String(health?.mode || state?.mode || 'PAPER')} />
        </div>

        <section className="card" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '14px', margin: '0 0 10px' }}>Live proof-gate ledger</h2>
          {gates.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {gates.map((gate, i) => {
                const ok = gate?.pass === true || String(gate?.status).toUpperCase() === 'PASS'
                return (
                  <div key={gate.gate_id || gate.label || i} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '8px 10px', background: 'var(--surface-2)', borderRadius: 6 }}>
                    <span style={{ fontSize: 12 }}>{gate.label || gate.name || gate.gate_id}</span>
                    <span className="num" style={{ color: ok ? 'var(--up)' : 'var(--amber)', fontSize: 11, fontWeight: 800 }}>
                      {String(gate.status || (ok ? 'PASS' : 'PENDING')).toUpperCase()}
                    </span>
                  </div>
                )
              })}
            </div>
          ) : (
            <PENDINGState
              tone="mut"
              title="NO GATE ROWS YET"
              reason="Waiting for /api/auto_gates. Analyzer is live; a dedicated prediction ledger is not enabled."
              dataTestId="prediction-audit-pending"
            />
          )}
        </section>
      </div>
    </div>
  )
}
