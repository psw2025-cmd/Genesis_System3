import React, { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { useStore } from '../../store';
import { MetricTile, PENDINGState, StatusChip } from './TruthUI';
import { formatIstStamp } from '../../lib/formatLive';
import { API_BASE, API_HEADERS } from '../../config';

type AccuracyTrend = {
  status?: string
  days_available?: number
  avg_rho?: number
  retrain_needed?: boolean
  trend?: Array<{
    date?: string
    rho?: number
    hit_rate?: number
    status?: string
    predicted?: string[]
    actual?: string[]
  }>
}

const BASE = API_BASE || window.location.origin

export const PredictionAudit: React.FC = () => {
  const { autoGates, state, health, lastSync } = useStore()
  const [accuracy, setAccuracy] = useState<AccuracyTrend | null>(null)
  const [accuracyError, setAccuracyError] = useState('')
  const [gateContract, setGateContract] = useState<any>(null)
  const effectiveGates = gateContract || autoGates
  const canonicalGates = effectiveGates?.gates && typeof effectiveGates.gates === 'object' ? effectiveGates.gates : {}
  const proofRows: any[] = Array.isArray(effectiveGates?.proof_gates)
    ? effectiveGates.proof_gates
    : Object.entries(effectiveGates?.gates || {}).map(([gate_id, gate]: [string, any]) => ({
        gate_id,
        label: gate_id,
        ...(typeof gate === 'object' ? gate : { status: gate }),
      }))
  const gates = proofRows.map((row) => {
    const canonical = canonicalGates[row?.gate_id]
    if (!canonical || typeof canonical !== 'object') return row
    const sourceConflict = row?.pass != null && canonical?.pass != null && Boolean(row.pass) !== Boolean(canonical.pass)
    return {
      ...row,
      ...canonical,
      label: row.label || row.name || row.gate_id,
      sourceConflict,
      status: canonical.pass === true ? 'PASS' : canonical.blocker_id ? 'BLOCKED' : 'NOT_PROVEN',
    }
  })
  const signal = state?.signals || {}
  const passCount = gates.filter((g) => g?.pass === true || String(g?.status).toUpperCase() === 'PASS').length
  const accuracyRows = Array.isArray(accuracy?.trend) ? accuracy.trend : []
  const latest = accuracyRows[accuracyRows.length - 1]
  const validationDays = Number(accuracy?.days_available || accuracy?.trend?.length || 0)
  const avgRho = Number(accuracy?.avg_rho)
  const hitRate = Number(latest?.hit_rate)
  const canonicalAccuracyGate = canonicalGates.ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS || {}
  const gateDays = Number(canonicalAccuracyGate.days_recorded || 0)
  const validationContractConflict = Boolean(accuracy) && gateDays > 0 && gateDays !== validationDays
  const validationProven = canonicalAccuracyGate.pass === true
    && validationDays >= 5
    && Number.isFinite(avgRho)
    && avgRho >= 0.7

  useEffect(() => {
    let cancelled = false
    const loadAccuracy = async () => {
      const fetchPath = async (path: string) => {
        const response = await fetch(BASE + path, {
          cache: 'no-store',
          credentials: 'include',
          headers: { Accept: 'application/json', ...API_HEADERS },
        })
        if (!response.ok) throw new Error(`${path} returned HTTP ${response.status}`)
        return response.json()
      }
      const [accuracyResult, gatesResult] = await Promise.allSettled([
        fetchPath('/api/accuracy_trend'),
        fetchPath('/api/auto_gates'),
      ])
      if (cancelled) return
      if (accuracyResult.status === 'fulfilled') {
        setAccuracy(accuracyResult.value)
        setAccuracyError('')
      } else {
        setAccuracyError(accuracyResult.reason?.message || String(accuracyResult.reason))
      }
      if (gatesResult.status === 'fulfilled') {
        setGateContract(gatesResult.value)
      }
    }
    void loadAccuracy()
    const timer = window.setInterval(loadAccuracy, 60_000)
    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [])

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

        <section className="card" data-testid="prediction-validation-summary" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
            <div>
              <h2 style={{ fontSize: '14px', margin: 0 }}>Prediction vs actual validation</h2>
              <p style={{ margin: '5px 0 0', color: 'var(--text-mut)', fontSize: 11 }}>
                Sources: /api/accuracy_trend + canonical /api/auto_gates · minimum proof gate: 5 days and average Spearman ρ ≥ 0.70
              </p>
            </div>
            <StatusChip
              label="VALIDATION"
              value={validationContractConflict ? 'DATA_CONTRACT_CONFLICT' : validationProven ? 'PASS' : accuracy ? 'NOT_PROVEN' : accuracyError ? 'ERROR' : 'LOADING'}
              status={validationProven ? 'ok' : validationContractConflict || accuracyError ? 'error' : 'warn'}
            />
          </div>
          {accuracy ? (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
                <MetricTile label="Sample size" value={`${validationDays} day${validationDays === 1 ? '' : 's'}`} tone={validationDays >= 5 ? 'ok' : 'warn'} />
                <MetricTile label="Average Spearman ρ" value={Number.isFinite(avgRho) ? avgRho.toFixed(2) : 'N/A'} tone={avgRho >= 0.7 ? 'ok' : 'warn'} />
                <MetricTile label="Latest hit rate" value={Number.isFinite(hitRate) ? `${(hitRate * 100).toFixed(1)}%` : 'N/A'} tone={hitRate >= 0.7 ? 'ok' : 'warn'} />
                <MetricTile label="Latest evaluated" value={latest?.date || 'N/A'} sub={String(latest?.status || 'NOT_PROVEN')} />
              </div>
              <div style={{ marginTop: 12, color: validationProven ? 'var(--up)' : 'var(--amber)', fontSize: 12, lineHeight: 1.5 }}>
                {validationContractConflict
                  ? `/api/accuracy_trend reports ${validationDays} day(s), while /api/auto_gates reports ${gateDays}. Promotion is blocked until the backend contracts reconcile.`
                  : validationProven
                  ? 'Validation threshold is met for the currently reported sample.'
                  : `Promotion remains blocked: ${validationDays}/5 days and ρ ${Number.isFinite(avgRho) ? avgRho.toFixed(2) : 'N/A'}/0.70. An impressive percentage without sample size is not proof.`}
              </div>
              {latest && (
                <div style={{ marginTop: 10, fontSize: 11, color: 'var(--text-mut)', overflowWrap: 'anywhere' }}>
                  Predicted: {(latest.predicted || []).join(', ') || 'N/A'} · Actual: {(latest.actual || []).join(', ') || 'N/A'}
                </div>
              )}
            </>
          ) : (
            <PENDINGState
              tone={accuracyError ? 'warn' : 'mut'}
              title={accuracyError ? 'ACCURACY CONTRACT ERROR' : 'LOADING VALIDATION'}
              reason={accuracyError || 'Waiting for /api/accuracy_trend.'}
              dataTestId="prediction-validation-pending"
            />
          )}
        </section>

        <section className="card" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '14px', margin: '0 0 10px' }}>Live proof-gate ledger</h2>
          {gates.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {gates.map((gate, i) => {
                const ok = gate?.pass === true || String(gate?.status).toUpperCase() === 'PASS'
                return (
                  <div key={gate.gate_id || gate.label || i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, padding: '8px 10px', background: 'var(--surface-2)', borderRadius: 6 }}>
                    <span style={{ minWidth: 0, fontSize: 12 }}>
                      <span>{gate.label || gate.name || gate.gate_id}</span>
                      <span style={{ display: 'block', marginTop: 3, color: gate.sourceConflict ? 'var(--down)' : 'var(--text-mut)', fontSize: 10 }}>
                        {gate.sourceConflict
                          ? 'CONTRACT CONFLICT: summary row disagrees with canonical gate'
                          : gate.note || gate.blocker_id || 'Canonical /api/auto_gates verdict'}
                      </span>
                    </span>
                    <span className="num" style={{ flexShrink: 0, color: ok ? 'var(--up)' : gate.sourceConflict ? 'var(--down)' : 'var(--amber)', fontSize: 11, fontWeight: 800 }}>
                      {gate.sourceConflict ? 'CONFLICT' : String(gate.status || (ok ? 'PASS' : 'NOT_PROVEN')).toUpperCase()}
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
