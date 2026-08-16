import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'

type LoadState = 'loading' | 'ready' | 'not_ready' | 'error'

type ModelRec = {
  status?: string
  model_proof_ready?: boolean
  total_predictions?: number
  avg_accuracy?: number | null
  avg_confidence?: number | null
  proof_pass_count?: number
  validation_pending_count?: number
  blocker_reason?: string
  message?: string
  generated_at_utc?: string
}

function mergeModels(performance: any, comparison: any): Record<string, ModelRec> {
  const out: Record<string, ModelRec> = {}
  const sources = [
    performance?.models,
    performance?.performance?.models,
    comparison?.models,
    comparison?.comparison?.models,
  ]
  for (const src of sources) {
    if (!src || typeof src !== 'object') continue
    for (const [name, rec] of Object.entries(src)) {
      if (name === 'status' || !rec || typeof rec !== 'object') continue
      out[name] = { ...(out[name] || {}), ...(rec as ModelRec) }
    }
  }
  return out
}

function fmtPct(v: number | null | undefined): string {
  if (v == null || Number.isNaN(Number(v))) return 'N/A'
  const n = Number(v)
  // Hit rates may already be 0–1 or 0–100
  const pct = n <= 1 ? n * 100 : n
  return `${pct.toFixed(2)}%`
}

export default function MLPerformance() {
  const [state, setState] = useState<Record<string, any> | null>(null)
  const [performance, setPerformance] = useState<Record<string, any> | null>(null)
  const [comparison, setComparison] = useState<Record<string, any> | null>(null)
  const [status, setStatus] = useState<LoadState>('loading')
  const [message, setMessage] = useState('Checking model artifacts...')

  useEffect(() => {
    let cancelled = false
    const fetchOnce = async () => {
      setStatus('loading')
      try {
        const stateRes = await axios.get(`${API_BASE}/api/state`, { timeout: 10000, headers: API_HEADERS })
        if (!cancelled) setState(stateRes.data)
      } catch {
        // State is useful but not enough to fail the tab.
      }

      const [perfRes, compRes] = await Promise.allSettled([
        axios.get(`${API_BASE}/api/ml/performance`, { timeout: 12000, headers: API_HEADERS }),
        axios.get(`${API_BASE}/api/ml/compare`, { timeout: 12000, headers: API_HEADERS }),
      ])
      if (cancelled) return

      const perfBody = perfRes.status === 'fulfilled' ? perfRes.value.data : null
      const compBody = compRes.status === 'fulfilled' ? compRes.value.data : null
      const perf = perfBody?.performance || perfBody
      const comp = compBody?.comparison || compBody
      setPerformance(perf)
      setComparison(comp)

      const models = mergeModels(perf, comp)
      const names = Object.keys(models)
      const proven = names.filter((n) => models[n]?.model_proof_ready === true)
      const apiReady = perfBody?.model_proof_ready === true || perf?.model_proof_ready === true
        || compBody?.model_proof_ready === true || comp?.model_proof_ready === true
        || proven.length > 0
      const apiMessage = perfBody?.message || perf?.message || compBody?.message || comp?.message

      if (apiReady) {
        setStatus('ready')
        setMessage(apiMessage || `Loaded ${proven.length} proven model performance record(s).`)
      } else if (names.length > 0) {
        setStatus('not_ready')
        setMessage(
          apiMessage
          || `Loaded ${names.length} validation-pending artifact(s). Model not proven — missing matured prediction history / post-market validation.`,
        )
      } else {
        setStatus('not_ready')
        setMessage(
          apiMessage
          || 'No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.',
        )
      }
    }
    fetchOnce().catch((err) => {
      if (cancelled) return
      setStatus('error')
      setMessage(`ML proof endpoints pending: ${err?.message || String(err)}`)
    })
    return () => { cancelled = true }
  }, [])

  const model = state?.model || {}
  const models = mergeModels(performance, comparison)
  const modelNames = Object.keys(models)
  const provenCount = modelNames.filter((n) => models[n]?.model_proof_ready === true).length
  const validationPendingCount = modelNames.length - provenCount
  const ready = status === 'ready'
  const badgeLabel = ready
    ? 'MODEL_PROOF_READY'
    : status === 'loading'
      ? 'CHECKING'
      : status === 'not_ready'
        ? 'MODEL_PROOF_VALIDATION_PENDING'
        : 'MODEL_NOT_PROVEN'
  const badgeColor = ready ? 'var(--up)' : status === 'loading' ? '#f59e0b' : 'var(--down)'
  const badgeBorder = ready ? 'rgba(16,185,129,.45)' : status === 'loading' ? 'rgba(245,158,11,.45)' : 'rgba(239,68,68,.45)'
  const badgeBg = ready ? 'rgba(16,185,129,.12)' : status === 'loading' ? 'rgba(245,158,11,.12)' : 'rgba(239,68,68,.12)'

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>ML Model Truth</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>This tab is proof-only. It does not train inline and does not invent metrics.</div>
        </div>
        <span style={{
          padding: '5px 10px', borderRadius: 999, fontSize: 11, fontWeight: 900,
          color: badgeColor,
          border: `1px solid ${badgeBorder}`,
          background: badgeBg,
        }}>{badgeLabel}</span>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ fontWeight: 900, marginBottom: 6 }}>{message}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
          Required proof: matured prediction history, post-market validation, accuracy/drift report, and retrain output. Without that, no 90% or money-ready claim is allowed.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(140px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Active model</div><div style={{ fontWeight: 900 }}>{model.active || 'NOT_PROVEN'}</div></div>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Fallback used</div><div style={{ fontWeight: 900 }}>{model.fallback_used === true ? 'YES' : model.fallback_used === false ? 'NO' : 'UNKNOWN'}</div></div>
        <div className="card">
          <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Proof records</div>
          <div style={{ fontWeight: 900 }}>{provenCount} proven / {validationPendingCount} validation pending</div>
        </div>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Training status</div><div style={{ fontWeight: 900 }}>{ready ? 'READY' : 'VALIDATION PENDING'}</div></div>
      </div>

      {ready && comparison?.best_model && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginTop: 0 }}>Best Model</h3>
          <div style={{ fontWeight: 900 }}>{comparison.best_model.name || 'N/A'}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Accuracy: {fmtPct(comparison.best_model.metrics?.avg_accuracy)}</div>
        </div>
      )}

      {modelNames.length > 0 ? (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Model Performance Records</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr>
                <th className="thead">Model</th>
                <th className="thead">Status</th>
                <th className="thead">Predictions</th>
                <th className="thead">Avg accuracy</th>
                <th className="thead">Proof pass / validation pending</th>
                <th className="thead">Blocker</th>
                <th className="thead">Generated</th>
              </tr>
            </thead>
            <tbody>{modelNames.map((name) => {
              const metrics = models[name] || {}
              const rowReady = metrics.model_proof_ready === true
              return (
                <tr key={name}>
                  <td className="tcell"><b>{name}</b></td>
                  <td className="tcell" style={{ color: rowReady ? 'var(--up)' : 'var(--down)', fontWeight: 700 }}>
                    {metrics.status || (rowReady ? 'READY' : 'VALIDATION_PENDING')}
                  </td>
                  <td className="tcell">{metrics.total_predictions ?? 0}</td>
                  <td className="tcell">{fmtPct(metrics.avg_accuracy)}</td>
                  <td className="tcell">{`${metrics.proof_pass_count ?? 0} / ${metrics.validation_pending_count ?? 0}`}</td>
                  <td className="tcell">{metrics.blocker_reason || metrics.message || (rowReady ? '—' : 'NOT_PROVEN')}</td>
                  <td className="tcell">{metrics.generated_at_utc || '—'}</td>
                </tr>
              )
            })}</tbody>
          </table>
        </div>
      ) : (
        <div style={{ border: '1px solid rgba(239,68,68,.35)', background: 'rgba(239,68,68,.08)', padding: 14, borderRadius: 10 }}>
          <b>Training proof missing.</b>
          <div style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: 12 }}>Next real fix is scheduler/model pipeline proof, not UI decoration.</div>
        </div>
      )}
    </div>
  )
}