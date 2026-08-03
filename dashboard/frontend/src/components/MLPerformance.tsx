import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'

type LoadState = 'loading' | 'ready' | 'not_ready' | 'error'

function getModelCount(payload: any): number {
  const models = payload?.performance?.models || payload?.models || payload?.comparison?.models || {}
  return models && typeof models === 'object' ? Object.keys(models).length : 0
}

function pct(value: any, digits = 2) {
  const number = Number(value)
  return Number.isFinite(number) ? `${(number * 100).toFixed(digits)}%` : '--'
}

function number(value: any, digits = 3) {
  const n = Number(value)
  return Number.isFinite(n) ? n.toFixed(digits) : '--'
}

function Metric({ label, value, sub }: { label: string; value: React.ReactNode; sub?: string }) {
  return (
    <div className="card">
      <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>{label}</div>
      <div style={{ fontWeight: 900, fontSize: 20, marginTop: 5 }}>{value}</div>
      {sub && <div style={{ color: 'var(--text-muted)', fontSize: 10, marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

export default function MLPerformance() {
  const [state, setState] = useState<any>(null)
  const [performance, setPerformance] = useState<any>(null)
  const [comparison, setComparison] = useState<any>(null)
  const [research, setResearch] = useState<any>(null)
  const [status, setStatus] = useState<LoadState>('loading')
  const [message, setMessage] = useState('Checking model artifacts...')

  useEffect(() => {
    let cancelled = false
    const fetchOnce = async () => {
      setStatus('loading')
      const [stateRes, perfRes, compRes, researchRes] = await Promise.allSettled([
        axios.get(`${API_BASE}/api/state`, { timeout: 10000, headers: API_HEADERS }),
        axios.get(`${API_BASE}/api/ml/performance`, { timeout: 12000, headers: API_HEADERS }),
        axios.get(`${API_BASE}/api/ml/compare`, { timeout: 12000, headers: API_HEADERS }),
        axios.get(`${API_BASE}/api/research/model-proof`, { timeout: 15000, headers: API_HEADERS }),
      ])
      if (cancelled) return
      setState(stateRes.status === 'fulfilled' ? stateRes.value.data : null)
      const perf = perfRes.status === 'fulfilled' ? (perfRes.value.data.performance || perfRes.value.data) : null
      const comp = compRes.status === 'fulfilled' ? (compRes.value.data.comparison || compRes.value.data) : null
      const proof = researchRes.status === 'fulfilled' ? researchRes.value.data : null
      setPerformance(perf)
      setComparison(comp)
      setResearch(proof)

      if (proof?.status === 'PASS') {
        setStatus('ready')
        setMessage('Full archive training, validation selection and frozen holdout proof loaded.')
      } else if (getModelCount(perf) + getModelCount(comp) > 0) {
        setStatus('ready')
        setMessage('Legacy model performance records loaded; full archive proof is not yet present.')
      } else {
        setStatus('not_ready')
        setMessage(proof?.message || 'No completed full archive model/backtest proof is available.')
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
  const frozen = research?.frozen_test || {}
  const cost80 = frozen?.cost_stress?.['80.0'] || {}
  const generation = research?.feature_generation || {}
  const split = research?.split || {}
  const tuning = research?.challenger_tuning || {}
  const assessment = research?.candidate_assessment || {}
  const selected = research?.selected_config || {}
  const ready = research?.status === 'PASS'

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>ML Model Truth</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>All numbers come from persisted proof artifacts. No model trains inside the browser.</div>
        </div>
        <span style={{
          padding: '5px 10px', borderRadius: 999, fontSize: 11, fontWeight: 900,
          color: ready ? 'var(--up)' : status === 'loading' ? '#f59e0b' : 'var(--down)',
          border: `1px solid ${ready ? 'rgba(16,185,129,.45)' : status === 'loading' ? 'rgba(245,158,11,.45)' : 'rgba(239,68,68,.45)'}`,
          background: ready ? 'rgba(16,185,129,.12)' : status === 'loading' ? 'rgba(245,158,11,.12)' : 'rgba(239,68,68,.12)',
        }}>{ready ? 'FROZEN_PROOF_COMPLETE' : status === 'loading' ? 'CHECKING' : 'MODEL_NOT_PROVEN'}</span>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ fontWeight: 900, marginBottom: 6 }}>{message}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
          Live trading and model promotion remain disabled. A positive historical result is a research candidate, not a profit guarantee.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12, marginBottom: 16 }}>
        <Metric label="Archive sessions" value={research?.archive_profile?.files ?? '--'} sub={`${research?.archive_profile?.rows ?? '--'} raw rows`} />
        <Metric label="Feature rows" value={generation?.tradable_feature_rows ?? '--'} sub={`${generation?.feature_files ?? '--'} feature sessions`} />
        <Metric label="Train / valid / test" value={`${split?.train_days ?? '--'} / ${split?.valid_days ?? '--'} / ${split?.test_days ?? '--'}`} sub="Chronological + embargo" />
        <Metric label="Frozen trades" value={cost80?.trades ?? frozen?.trades ?? '--'} sub="Untouched final holdout" />
        <Metric label="Frozen win rate" value={pct(cost80?.win_rate)} sub="80 bps total cost" />
        <Metric label="Profit factor" value={number(cost80?.profit_factor)} sub="80 bps total cost" />
        <Metric label="Sharpe / Sortino" value={`${number(cost80?.annualized_sharpe)} / ${number(cost80?.annualized_sortino)}`} />
        <Metric label="Max drawdown" value={pct(cost80?.max_drawdown)} />
        <Metric label="Median daily Spearman" value={number(frozen?.median_daily_spearman)} />
        <Metric label="ROC AUC / Brier" value={`${number(frozen?.row_roc_auc)} / ${number(frozen?.row_brier)}`} />
        <Metric label="Walk-forward folds" value={`${research?.walk_forward?.folds_executed ?? 0}/${research?.walk_forward?.folds_requested ?? 0}`} />
        <Metric label="Research gates" value={`${assessment?.gates_passed ?? 0}/${assessment?.gates_total ?? 0}`} sub={assessment?.research_candidate ? 'Candidate only' : 'Blocked'} />
      </div>

      {ready && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginTop: 0 }}>Selected Ensemble</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 10, fontSize: 12 }}>
            <div>LightGBM weight: <b>{selected?.lightgbm_weight ?? '--'}</b></div>
            <div>Top-K: <b>{selected?.top_k ?? '--'}</b></div>
            <div>Minimum probability: <b>{selected?.min_probability ?? '--'}</b></div>
            <div>Optuna trials: <b>{tuning?.optuna_trials ?? '--'}</b></div>
            <div>LightGBM sample rows: <b>{tuning?.train_sample_rows ?? '--'}</b></div>
            <div>Model SHA-256: <b style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>{research?.model_sha256 || '--'}</b></div>
          </div>
        </div>
      )}

      {comparison?.best_model && !ready && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginTop: 0 }}>Legacy Best Model</h3>
          <div style={{ fontWeight: 900 }}>{comparison.best_model.name || 'N/A'}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Accuracy: {comparison.best_model.metrics?.avg_accuracy ? `${(comparison.best_model.metrics.avg_accuracy * 100).toFixed(2)}%` : 'N/A'}</div>
        </div>
      )}

      {!ready && performance?.models && Object.keys(performance.models).length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Legacy Model Performance Records ({modelCount})</h3>
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
      )}

      {!ready && model.active && <div style={{ marginTop: 12, color: 'var(--text-muted)', fontSize: 11 }}>Runtime model: {model.active}</div>}
    </div>
  )
}
