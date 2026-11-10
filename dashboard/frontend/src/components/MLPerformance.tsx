import { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'
import { useStore } from '../store'
import { ValidationChecklist, showField, type ChecklistItem } from './ValidationChecklist'
import { PendingLifecycleBanner } from './PendingLifecycleBanner'

type LoadState = 'loading' | 'ready' | 'not_ready' | 'error'

type ModelRec = {
  status?: string
  model_proof_ready?: boolean
  total_predictions?: number | null
  avg_accuracy?: number | null
  avg_confidence?: number | null
  avg_spearman_rho?: number | null
  spearman_rho?: number | null
  proof_pass_count?: number | null
  validation_pending_count?: number | null
  blocker_reason?: string
  message?: string
  generated_at_utc?: string
  ready_for_live?: boolean
  hit_rate?: number | null
  direction_hit_rate?: number | null
}

type PerfBody = {
  status?: string
  proof_status?: string
  message?: string
  ready_for_live?: boolean
  ready_for_live_reason?: string
  rho?: number | null
  hit_rate?: number | null
  proof_pass_count?: number | null
  generated_at_utc?: string | null
  blocker_reason?: string | null
  blocker_reasons?: { model?: string; blocker_reason?: string }[]
  validations_checklist?: ChecklistItem[]
  performance?: {
    models?: Record<string, ModelRec>
    status?: string
    message?: string
    ready_for_live?: boolean
    ready_for_live_reason?: string
    rho?: number | null
    hit_rate?: number | null
    proof_pass_count?: number | null
    generated_at_utc?: string | null
    validations_checklist?: ChecklistItem[]
  }
  models?: Record<string, ModelRec>
}

function mergeModels(performance: PerfBody['performance'] | null, comparison: any): Record<string, ModelRec> {
  const out: Record<string, ModelRec> = {}
  const sources = [
    performance?.models,
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

export default function MLPerformance() {
  const [state, setState] = useState<any>(null)
  const [perfBody, setPerfBody] = useState<PerfBody | null>(null)
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

      const body: PerfBody | null = perfRes.status === 'fulfilled' ? perfRes.value.data : null
      const compBody = compRes.status === 'fulfilled' ? compRes.value.data : null
      const perf = body?.performance || null
      const comp = compBody?.comparison || compBody
      setPerfBody(body)
      setComparison(comp)

      const models = mergeModels(perf, comp)
      const names = Object.keys(models)
      const apiStatus = String(body?.proof_status || perf?.status || body?.status || '')
      const apiMessage = body?.message || perf?.message || compBody?.message || comp?.message
      const liveReady = body?.ready_for_live === true || perf?.ready_for_live === true

      if (liveReady && apiStatus && apiStatus !== 'BLOCKED') {
        setStatus('ready')
        setMessage(apiMessage || 'Forward validation is ready_for_live.')
      } else if (body || names.length > 0) {
        setStatus('not_ready')
        setMessage(apiMessage || 'Model performance is blocked.')
      } else {
        setStatus('not_ready')
        setMessage(apiMessage || 'No matured ML training/performance artifact is available.')
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
  const perf = perfBody?.performance || null
  const models = mergeModels(perf, comparison)
  const modelNames = Object.keys(models)
  const liveReady = perfBody?.ready_for_live === true || perf?.ready_for_live === true
  const apiStatus = String(perfBody?.proof_status || perf?.status || (status === 'loading' ? 'CHECKING' : 'BLOCKED'))
  const reason = perfBody?.ready_for_live_reason || perf?.ready_for_live_reason
  const checklist = perfBody?.validations_checklist || perf?.validations_checklist
  const rho = perfBody?.rho ?? perf?.rho
  const hitRate = perfBody?.hit_rate ?? perf?.hit_rate
  const proofPass = perfBody?.proof_pass_count ?? perf?.proof_pass_count
  const generated = perfBody?.generated_at_utc || perf?.generated_at_utc
  const badgeColor = liveReady ? 'var(--up)' : 'var(--down)'

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <PendingLifecycleBanner />
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>ML Model Truth</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>This tab is proof-only. It does not train inline and does not invent metrics.</div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <span
            data-testid="ml-status"
            style={{
              padding: '5px 10px', borderRadius: 999, fontSize: 11, fontWeight: 900,
              color: apiStatus === 'BLOCKED' || !liveReady ? 'var(--down)' : 'var(--up)',
              border: '1px solid rgba(239,68,68,.45)',
              background: 'rgba(239,68,68,.12)',
            }}
          >{apiStatus}</span>
          <span
            data-testid="ready-for-live"
            style={{
              padding: '5px 10px', borderRadius: 999, fontSize: 11, fontWeight: 900,
              color: badgeColor,
              border: `1px solid ${liveReady ? 'rgba(16,185,129,.45)' : 'rgba(239,68,68,.45)'}`,
              background: liveReady ? 'rgba(16,185,129,.12)' : 'rgba(239,68,68,.12)',
            }}
          >ready_for_live={showField(perfBody?.ready_for_live ?? perf?.ready_for_live)}</span>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ fontWeight: 900, marginBottom: 6 }}>{message}</div>
        <div data-testid="ready-for-live-reason" style={{ fontSize: 12, lineHeight: 1.45 }}>{showField(reason)}</div>
        <button
          type="button"
          onClick={() => useStore.getState().setActiveTab('system-readiness')}
          style={{ marginTop: 10, fontSize: 12, fontWeight: 700 }}
        >
          System readiness
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(140px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>rho</div><div style={{ fontWeight: 900 }} data-testid="ml-rho">{showField(rho)}</div></div>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>hit_rate</div><div style={{ fontWeight: 900 }} data-testid="ml-hit-rate">{showField(hitRate)}</div></div>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>proof_pass_count</div><div style={{ fontWeight: 900 }}>{showField(proofPass)}</div></div>
        <div className="card"><div style={{ color: 'var(--text-muted)', fontSize: 11 }}>generated_at_utc</div><div style={{ fontWeight: 900, fontSize: 12 }}>{showField(generated)}</div></div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>Active model / fallback</div>
        <div style={{ fontWeight: 700 }}>{showField(model.active)} · fallback {model.fallback_used === true ? 'YES' : model.fallback_used === false ? 'NO' : 'null'}</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Validation checklist</h3>
        <ValidationChecklist items={checklist} />
      </div>

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
                <th className="thead">reported rho</th>
                <th className="thead">hit_rate</th>
                <th className="thead">Proof pass</th>
                <th className="thead">Blocker</th>
                <th className="thead">Generated</th>
              </tr>
            </thead>
            <tbody>{modelNames.map((name) => {
              const metrics = models[name] || {}
              const reportedRho = metrics.avg_spearman_rho ?? metrics.spearman_rho
              const reportedHit = metrics.hit_rate ?? metrics.direction_hit_rate
              return (
                <tr key={name}>
                  <td className="tcell"><b>{name}</b></td>
                  <td className="tcell" style={{ color: 'var(--down)', fontWeight: 700 }}>{showField(metrics.status)}</td>
                  <td className="tcell">{showField(metrics.total_predictions)}</td>
                  <td className="tcell">{showField(metrics.avg_accuracy)}</td>
                  <td className="tcell">{showField(reportedRho)}</td>
                  <td className="tcell">{showField(reportedHit)}</td>
                  <td className="tcell">{showField(metrics.proof_pass_count)}</td>
                  <td className="tcell" data-testid={`blocker-${name}`}>{showField(metrics.blocker_reason || metrics.message)}</td>
                  <td className="tcell">{showField(metrics.generated_at_utc)}</td>
                </tr>
              )
            })}</tbody>
          </table>
        </div>
      ) : (
        <div style={{ border: '1px solid rgba(239,68,68,.35)', background: 'rgba(239,68,68,.08)', padding: 14, borderRadius: 10 }}>
          <b>Training proof missing.</b>
          <div style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: 12 }}>No model records were returned by /api/ml/performance.</div>
        </div>
      )}
    </div>
  )
}
