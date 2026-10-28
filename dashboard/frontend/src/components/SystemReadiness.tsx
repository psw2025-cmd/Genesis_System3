import { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'
import { ValidationChecklist, showField, type ChecklistItem } from './ValidationChecklist'
import { PendingLifecycleBanner } from './PendingLifecycleBanner'

type GitRef = { ref?: string; sha?: string | null; error?: string | null }

type ReadinessPayload = {
  banner?: string
  deploy_allowed?: boolean
  local_git?: { head?: GitRef; origin_main?: GitRef }
  live_trading_enabled?: string
  dhan_pin_warning?: string | null
  dockerignore?: {
    present?: boolean
    market_validations_exception?: boolean
    paper_validations_exception?: boolean
    both?: boolean
  }
  owner_approval?: {
    present?: boolean
    approved_at?: string | null
    committed?: boolean | null
    detail?: string
  }
  github_checks?: {
    ok?: boolean
    error?: string | null
    pull_requests?: unknown
    main_status?: { state?: string | null; sha?: string | null; statuses?: { context?: string; state?: string }[] } | null
  }
  local_ml_performance?: {
    ready_for_live?: boolean
    status?: string
    message?: string
    ready_for_live_reason?: string
    rho?: number | null
    hit_rate?: number | null
    proof_pass_count?: number | null
    generated_at_utc?: string | null
    blocker_reasons?: { model?: string; blocker_reason?: string }[]
    validations_checklist?: ChecklistItem[]
  }
  cloud_ml_performance?: {
    ok?: boolean
    url?: string
    ready_for_live?: boolean | null
    status?: string | null
    message?: string | null
    error?: string | null
  }
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>{label}</span>
      <span style={{ fontSize: 12, fontWeight: 700, textAlign: 'right', wordBreak: 'break-word' }}>{value}</span>
    </div>
  )
}

export default function SystemReadiness() {
  const [payload, setPayload] = useState<ReadinessPayload | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    axios.get(`${API_BASE}/api/system/readiness`, { timeout: 25000, headers: API_HEADERS })
      .then((res) => {
        if (!cancelled) {
          setPayload(res.data)
          setError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message || String(err))
      })
    return () => { cancelled = true }
  }, [])

  const local = payload?.local_ml_performance
  const ready = local?.ready_for_live === true
  const head = payload?.local_git?.head
  const originMain = payload?.local_git?.origin_main
  const cloud = payload?.cloud_ml_performance
  const approval = payload?.owner_approval
  const checks = payload?.github_checks
  const docker = payload?.dockerignore

  return (
    <div data-testid="system-readiness" style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <PendingLifecycleBanner />
      <h2 style={{ margin: '0 0 8px', fontSize: 22 }}>System readiness</h2>
      <div
        data-testid="deploy-blocked-banner"
        style={{
          marginBottom: 16,
          padding: 12,
          borderRadius: 10,
          border: '1px solid rgba(239,68,68,.45)',
          background: 'rgba(239,68,68,.1)',
          color: 'var(--down)',
          fontWeight: 800,
        }}
      >
        {payload?.banner || (error ? 'Readiness payload unavailable.' : 'Loading readiness…')}
        <div style={{ marginTop: 6, fontWeight: 600, fontSize: 12 }}>
          deploy_allowed={showField(payload?.deploy_allowed)} · this page has no deploy control
        </div>
      </div>

      {payload?.dhan_pin_warning && (
        <div data-testid="dhan-pin-warning" style={{ marginBottom: 16, padding: 12, borderRadius: 10, border: '1px solid rgba(245,158,11,.45)', background: 'rgba(245,158,11,.1)' }}>
          {payload.dhan_pin_warning}
        </div>
      )}

      {error && (
        <div className="card" style={{ marginBottom: 16, color: 'var(--down)' }}>
          /api/system/readiness failed: {error}
        </div>
      )}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Local git</h3>
        <Row label="HEAD" value={head?.sha || head?.error || 'null'} />
        <Row label="origin/main" value={originMain?.sha || originMain?.error || 'null'} />
        <div style={{ color: 'var(--text-muted)', fontSize: 11, marginTop: 6 }}>
          SHA is read from git at request time. origin/main is the local ref when it already exists.
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }} data-testid="local-ml-performance">
        <h3 style={{ marginTop: 0 }}>Local /api/ml/performance</h3>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
          <span style={{ padding: '4px 8px', borderRadius: 999, fontWeight: 900, fontSize: 11, color: 'var(--down)', border: '1px solid rgba(239,68,68,.45)', background: 'rgba(239,68,68,.12)' }}>
            {local?.status || 'null'}
          </span>
          <span
            data-testid="ready-for-live"
            style={{
              padding: '4px 8px',
              borderRadius: 999,
              fontWeight: 900,
              fontSize: 11,
              color: ready ? 'var(--up)' : 'var(--down)',
              border: `1px solid ${ready ? 'rgba(16,185,129,.45)' : 'rgba(239,68,68,.45)'}`,
              background: ready ? 'rgba(16,185,129,.12)' : 'rgba(239,68,68,.12)',
            }}
          >
            ready_for_live={showField(local?.ready_for_live)}
          </span>
        </div>
        <Row label="rho" value={showField(local?.rho)} />
        <Row label="hit_rate" value={showField(local?.hit_rate)} />
        <Row label="proof_pass_count" value={showField(local?.proof_pass_count)} />
        <Row label="generated_at_utc" value={showField(local?.generated_at_utc)} />
        <div style={{ marginTop: 8, fontSize: 12, lineHeight: 1.45 }}>{showField(local?.ready_for_live_reason)}</div>
        <ul style={{ margin: '8px 0 0', paddingLeft: 18, fontSize: 12 }}>
          {(local?.blocker_reasons || []).map((row) => (
            <li key={`${row.model}-${row.blocker_reason}`}>{row.model}: {showField(row.blocker_reason)}</li>
          ))}
        </ul>
        <div style={{ marginTop: 12 }}>
          <ValidationChecklist items={local?.validations_checklist} />
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }} data-testid="cloud-ml-performance">
        <h3 style={{ marginTop: 0 }}>Cloud /api/ml/performance</h3>
        <Row label="url" value={cloud?.url || 'null'} />
        <Row label="ready_for_live" value={showField(cloud?.ready_for_live)} />
        <Row label="status" value={showField(cloud?.status)} />
        <div style={{ marginTop: 8, fontSize: 12 }}>{cloud?.error ? cloud.error : showField(cloud?.message)}</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>.dockerignore validation exceptions</h3>
        <Row label="file present" value={showField(docker?.present)} />
        <Row label="state/market_validations exception" value={showField(docker?.market_validations_exception)} />
        <Row label="state/paper_validations exception" value={showField(docker?.paper_validations_exception)} />
      </div>

      <div className="card" style={{ marginBottom: 16 }} data-testid="owner-approval">
        <h3 style={{ marginTop: 0 }}>Owner approval</h3>
        <Row label="paragraph present" value={showField(approval?.present)} />
        <Row label="approved at" value={showField(approval?.approved_at)} />
        <Row label="in HEAD" value={showField(approval?.committed)} />
        <div style={{ marginTop: 8, fontSize: 12 }}>{approval?.detail || 'null'}</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }} data-testid="github-checks">
        <h3 style={{ marginTop: 0 }}>GitHub checks</h3>
        {checks?.error && <div style={{ color: 'var(--down)', fontSize: 12, marginBottom: 8 }}>{checks.error}</div>}
        <Row label="main combined state" value={showField(checks?.main_status?.state)} />
        <Row label="main sha" value={showField(checks?.main_status?.sha)} />
        <ul style={{ margin: '8px 0 0', paddingLeft: 18, fontSize: 12 }}>
          {(checks?.main_status?.statuses || []).length === 0 && <li>main statuses: null</li>}
          {(checks?.main_status?.statuses || []).map((row) => (
            <li key={`${row.context}-${row.state}`}>{row.context || 'null'}: {row.state || 'null'}</li>
          ))}
        </ul>
        <pre style={{ whiteSpace: 'pre-wrap', fontSize: 11, marginTop: 8 }}>
          {checks?.pull_requests == null ? 'open pull requests: null' : JSON.stringify(checks.pull_requests, null, 2)}
        </pre>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Process safety</h3>
        <Row label="LIVE_TRADING_ENABLED" value={showField(payload?.live_trading_enabled)} />
      </div>
    </div>
  )
}
