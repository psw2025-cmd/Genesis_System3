import { useEffect, useState } from 'react'
import { API_BASE, API_HEADERS } from '../config'

const BASE = API_BASE || (typeof window !== 'undefined' ? window.location.origin : '')

type ClosureCard = {
  id: string
  severity?: string
  defect?: string
  evidence?: string
  status_note?: string
  state?: string
  source?: string
}

type ClosureReport = {
  summary?: {
    open?: number
    resolved?: number
    in_progress?: number
    total_cards?: number
    next?: string
    serving_sha?: string
    gates?: string
  }
  phases?: {
    auto_resume?: {
      next_id?: string
      defect?: string
      instruction?: string
      state?: string
    }
    blocker_cards?: ClosureCard[]
    multi_source_verify?: {
      contracts?: Record<string, unknown>
      sources?: Record<string, { ok?: boolean }>
    }
    watchdog?: { status?: string; banner_required?: boolean }
  }
  generated_at_utc?: string
}

function toneFor(state?: string) {
  const s = String(state || '').toUpperCase()
  if (s === 'RESOLVED') return 'var(--up)'
  if (s === 'IN_PROGRESS') return 'var(--accent)'
  return 'var(--amber)'
}

export function ContinuousClosureBoard() {
  const [report, setReport] = useState<ClosureReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const r = await fetch(`${BASE}/api/continuous_closure?live=true`, {
          credentials: 'include',
          headers: { Accept: 'application/json', ...API_HEADERS },
        })
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const body = (await r.json()) as ClosureReport
        if (!cancelled) {
          setReport(body)
          setError(null)
        }
      } catch (e: any) {
        if (!cancelled) setError(String(e?.message || e))
      }
    }
    load()
    const t = window.setInterval(load, 120000)
    return () => {
      cancelled = true
      window.clearInterval(t)
    }
  }, [])

  const cards = Array.isArray(report?.phases?.blocker_cards) ? report!.phases!.blocker_cards! : []
  const openCards = cards.filter((c) => c.state !== 'RESOLVED').slice(0, 8)
  const resume = report?.phases?.auto_resume
  const summary = report?.summary
  const sources = report?.phases?.multi_source_verify?.sources || {}

  return (
    <section
      data-testid="continuous-closure-board"
      className="card"
      style={{ padding: 16, marginTop: 12 }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 10 }}>
        <div>
          <div className="panel-title">Continuous Closure · Blocker Cards</div>
          <div style={{ fontSize: 11, color: 'var(--text-mut)', marginTop: 4 }}>
            Repo-first scan · multi-source verify · watchdog · auto-resume
            {summary?.gates ? ` · Gates ${summary.gates}` : ''}
            {summary?.serving_sha ? ` · SHA ${String(summary.serving_sha).slice(0, 12)}` : ''}
          </div>
        </div>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono, monospace)', color: 'var(--text-sec)' }}>
          OPEN {summary?.open ?? '—'} · DONE {summary?.resolved ?? '—'} · NEXT {summary?.next || '—'}
        </div>
      </div>

      {error && (
        <div style={{ color: 'var(--amber)', fontSize: 12, marginBottom: 8 }}>
          Closure feed unavailable: {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12, fontSize: 11 }}>
        {(['repo', 'reports', 'live'] as const).map((k) => {
          const ok = Boolean(sources?.[k]?.ok)
          return (
            <span
              key={k}
              style={{
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '2px 8px',
                color: ok ? 'var(--up)' : 'var(--amber)',
              }}
            >
              {k.toUpperCase()} {ok ? 'OK' : 'GAP'}
            </span>
          )
        })}
        <span style={{ border: '1px solid var(--border)', borderRadius: 6, padding: '2px 8px' }}>
          WATCHDOG {report?.phases?.watchdog?.status || '—'}
        </span>
      </div>

      {resume && (
        <div
          data-testid="auto-resume-card"
          style={{
            marginBottom: 12,
            padding: 10,
            border: '1px solid rgba(120,180,255,.35)',
            borderRadius: 8,
            background: 'rgba(10,36,64,.45)',
          }}
        >
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent)' }}>AUTO-RESUME</div>
          <div style={{ fontSize: 13, marginTop: 4, color: 'var(--text-pri)' }}>
            Next: <strong>{resume.next_id}</strong> · {resume.state}
          </div>
          <div style={{ fontSize: 11, marginTop: 4, color: 'var(--text-mut)' }}>{resume.defect}</div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
        {openCards.length === 0 && !error && (
          <div style={{ fontSize: 12, color: 'var(--text-mut)' }}>No open blocker cards in feed.</div>
        )}
        {openCards.map((card) => (
          <div
            key={`${card.source}-${card.id}`}
            data-testid={`blocker-card-${card.id}`}
            style={{
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: 10,
              background: 'rgba(0,0,0,.18)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ fontWeight: 700, fontSize: 12 }}>{card.id}</span>
              <span style={{ fontSize: 10, color: toneFor(card.state) }}>{card.state}</span>
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-mut)', marginTop: 2 }}>
              {card.severity} · {card.source}
            </div>
            <div style={{ fontSize: 12, marginTop: 6, color: 'var(--text-pri)', lineHeight: 1.35 }}>
              {card.defect || card.status_note}
            </div>
            {card.evidence && (
              <div style={{ fontSize: 10, marginTop: 6, color: 'var(--text-mut)', overflowWrap: 'anywhere' }}>
                {card.evidence}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
