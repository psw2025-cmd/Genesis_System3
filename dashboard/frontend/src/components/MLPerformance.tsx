import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'

type LoadState = 'loading' | 'ready' | 'not_ready' | 'error'

function getModelCount(payload: any): number {
  const models = payload?.performance?.models || payload?.models || payload?.comparison?.models || {}
  return models && typeof models === 'object' ? Object.keys(models).length : 0
}

export default function MLPerformance() {
  const [state, setState] = useState<any>(null)
  const [performance, setPerformance] = useState<any>(null)
  const [comparison, setComparison] = useState<any>(null)
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

      const perf = perfRes.status === 'fulfilled' ? (perfRes.value.data.performance || perfRes.value.data) : null
      const comp = compRes.status === 'fulfilled' ? (compRes.value.data.comparison || compRes.value.data) : null
      setPerformance(perf)
      setComparison(comp)

      const modelCount = getModelCount(perf) + getModelCount(comp)
      if (modelCount > 0) {
        setStatus('ready')
        setMessage(`Loaded ${modelCount} model performance record(s).`)
      } else {
        setStatus('not_ready')
        setMessage('No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.')
      }
    }
    fetchOnce().catch((err) => {
      if (cancelled) return
      setStatus('error')
      setMessage(`ML proof endpoints unavailable: ${err?.message || String(err)}`)
    })
    return () => { cancelled = true }
  }, [])

  const model = state?.model || {}
  const modelCount = getModelCount(performance) + getModelCount(comparison)
  const ready = status === 'ready'

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>ML Model Truth</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>This tab is proof-only. It does not train inline and does not fake metrics.</div>
        </div>
        <span style={{
          padding: '5px 10px', borderRadius: 999, fontSize: 11, fontWeight: 900,
          color: ready ? 'var(--up)' : status === 'loading' ? '#f59e0b' : 'var(--down)',
          border: `1px solid ${ready ? 'rgba(16,185,129,.45)' : status === 'loading' ? 'rgba(245,158,11,.45)' : 'rgba(239,68,68,.45)'}`,
          background: ready ? 'rgba(16,185,129,.12)' : status === 'loading' ? 'rgba(245,158,11,.12)' : 'rgba(239,68,68,.12)',
        }}>{ready ? 'MODEL_PROOF_READY' : status === 'loading' ? 'CHECKING' : 'MODEL_NOT_PROVEN'}</span>
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
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Proof records</div><div style={{ fontWeight: 900 }}>{modelCount}</div></div>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Training status</div><div style={{ fontWeight: 900 }}>{ready ? 'PROVEN' : 'BLOCKED'}</div></div>
      </div>

      {comparison?.best_model && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginTop: 0 }}>Best Model</h3>
          <div style={{ fontWeight: 900 }}>{comparison.best_model.name || 'N/A'}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Accuracy: {comparison.best_model.metrics?.avg_accuracy ? `${(comparison.best_model.metrics.avg_accuracy * 100).toFixed(2)}%` : 'N/A'}</div>
        </div>
      )}

      {performance?.models && Object.keys(performance.models).length > 0 ? (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Model Performance Records</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead><tr><th className="thead">Model</th><th className="thead">Predictions</th><th className="thead">Avg accuracy</th><th className="thead">Avg confidence</th></tr></thead>
            <tbody>{Object.entries(performance.models).map(([name, metrics]: [string, any]) => (
              <tr key={name}>
                <td className="tcell"><b>{name}</b></td>
                <td className="tcell">{metrics?.total_predictions || 0}</td>
                <td className="tcell">{metrics?.avg_accuracy ? `${(metrics.avg_accuracy * 100).toFixed(2)}%` : 'N/A'}</td>
                <td className="tcell">{metrics?.avg_confidence ? `${(metrics.avg_confidence * 100).toFixed(2)}%` : 'N/A'}</td>
              </tr>
            ))}</tbody>
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
