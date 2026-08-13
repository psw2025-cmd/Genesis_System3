import React, { useState } from 'react'
import { Sparkles } from 'lucide-react'
import { useStore } from '../../store'
import { formatInr, formatIstStamp } from '../../lib/formatLive'
import { humanizeContractReason, resolveFeedQuality } from '../../lib/feedQuality'
import { brokerIsConnected } from '../../lib/healthTruth'

export const MultibaggerResearch: React.FC = () => {
  const {
    research, state, health, paper, pnl, marketOpen, wsStatus, brokerConnected, setActiveTab,
  } = useStore()
  const [showCriteria, setShowCriteria] = useState(false)

  const contract = research || {}
  const status = String(contract.status || 'loading').toLowerCase()
  const candidates: any[] = Array.isArray(contract.candidates) ? contract.candidates : []
  const sections = contract.sections && typeof contract.sections === 'object' ? contract.sections : {}
  const ready = candidates.length > 0
  const totalPnl = paper?.pnl?.summary?.total_pnl ?? pnl?.summary?.total_pnl ?? state?.pnl?.total ?? state?.pnl?.unrealized
  const pnlNum = Number(totalPnl)
  const pnlTone = Number.isFinite(pnlNum) ? (pnlNum < 0 ? 'error' : pnlNum > 0 ? 'ok' : 'mut') : 'mut'
  const tickAge = state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec
  const feed = resolveFeedQuality({
    marketOpen,
    wsStatus,
    tickAgeSec: tickAge,
    dataSource: state?.data_source || health?.data_source,
    brokerConnected: brokerIsConnected(health, brokerConnected),
  })
  const researchStatus = ready
    ? `${candidates.length} verified candidate${candidates.length === 1 ? '' : 's'}`
    : status === 'partial'
      ? 'Partial evidence — ranking incomplete'
      : status === 'stale'
        ? 'Evidence contract is stale'
        : 'Waiting for verified candidates'
  const reason = humanizeContractReason(contract.reason)
  const nextOpen = state?.market?.next_open || health?.market?.next_open
  const lastFetch = formatIstStamp(state?.last_fetch_ts_iso || contract.as_of)

  return (
    <div data-testid="multibagger-root" className="workspace-page">
      <header className="workspace-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
          <Sparkles size={18} color="var(--accent)" aria-hidden />
          <div>
            <h1 className="workspace-h1">Multibagger research</h1>
            <p className="workspace-lead">{researchStatus}</p>
          </div>
        </div>
        <span className={`feed-badge feed-badge-${feed.tone}`} title={feed.detail}>{feed.label}</span>
      </header>

      <div className="workspace-body">
        <section className="hero-panel" aria-label="Candidates summary">
          <div className="hero-main">
            <div className="metric-label">Candidates</div>
            <div className="hero-value num" data-testid="multibagger-candidate-count">{candidates.length}</div>
            <p className="hero-copy">
              {ready
                ? 'Provenance-valid symbols from the research contract.'
                : 'Primary research board for verified multibagger candidates.'}
            </p>
          </div>
          <div className="hero-metrics">
            <div className={`metric-quiet metric-${pnlTone}`}>
              <div className="metric-label">P&amp;L</div>
              <div className="num metric-strong">{formatInr(totalPnl)}</div>
              <div className="metric-hint">Paper / analyzer</div>
            </div>
            <div className="metric-quiet">
              <div className="metric-label">Exposure</div>
              <div className="num metric-strong">{formatInr(state?.risk?.exposure)}</div>
              <div className="metric-hint">Read-only portfolio</div>
            </div>
            <div className="metric-quiet">
              <div className="metric-label">Updated</div>
              <div className="num metric-strong" style={{ fontSize: 15 }}>{lastFetch}</div>
              <div className="metric-hint">{feed.detail}</div>
            </div>
          </div>
        </section>

        {ready ? (
          <section className="elevated-panel" style={{ padding: 20, overflowX: 'auto' }}>
            <h2 className="section-title">Verified candidates</h2>
            <table className="clean-table">
              <thead>
                <tr>
                  <th style={{ textAlign: 'left' }}>Rank</th>
                  <th style={{ textAlign: 'left' }}>Symbol</th>
                  <th style={{ textAlign: 'right' }}>Price</th>
                  <th style={{ textAlign: 'left' }}>Model</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((row) => (
                  <tr key={row.candidate_id || row.symbol}>
                    <td>{row.rank ?? '—'}</td>
                    <td>{row.symbol ?? '—'}</td>
                    <td className="num" style={{ textAlign: 'right' }}>{formatInr(row.price?.value)}</td>
                    <td>{row.model?.name ? `${row.model.name} ${row.model.version || ''}`.trim() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        ) : (
          <section className="elevated-panel empty-research" data-testid="multibagger-pending">
            <h2 className="section-title">No verified candidates yet</h2>
            <p className="empty-reason">{reason}</p>
            <dl className="empty-facts">
              <div>
                <dt>Last updated</dt>
                <dd className="num">{lastFetch}</dd>
              </div>
              <div>
                <dt>Data status</dt>
                <dd>{feed.label} · {brokerIsConnected(health, brokerConnected) ? 'Broker connected' : 'Broker disconnected'} · {marketOpen ? 'Market open' : 'Market closed'}</dd>
              </div>
              <div>
                <dt>Source</dt>
                <dd>{state?.data_source || health?.data_source || contract.source || 'Research contract pending'}</dd>
              </div>
              <div>
                <dt>Next market open</dt>
                <dd>{nextOpen ? String(nextOpen) : 'Not reported by the market calendar'}</dd>
              </div>
            </dl>
            {Object.keys(sections).length > 0 && (
              <div className="section-chips" aria-label="Research sections">
                {Object.entries(sections).map(([key, value]) => (
                  <span key={key} className="quiet-chip">
                    {key.replace(/_/g, ' ')} · {String(value)}
                  </span>
                ))}
              </div>
            )}
            <div className="empty-actions">
              <button type="button" className="btn-primary" onClick={() => setActiveTab('data-integrity')}>
                View data integrity
              </button>
              <button type="button" className="btn-secondary" onClick={() => setShowCriteria((v) => !v)} aria-expanded={showCriteria}>
                {showCriteria ? 'Hide research criteria' : 'View research criteria'}
              </button>
            </div>
            {showCriteria && (
              <div className="criteria-panel" role="region" aria-label="Research criteria">
                <p style={{ margin: '0 0 8px', fontSize: 13, color: 'var(--text-sec)' }}>
                  Candidates appear only when a producer supplies provenance-valid evidence. Forecast probabilities are never invented from analyzer P&amp;L.
                </p>
                <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-sec)', fontSize: 13, lineHeight: 1.55 }}>
                  <li>Identity: candidate id, symbol, and positive integral rank</li>
                  <li>Price: INR value from an approved source with a fresh observation time</li>
                  <li>Model: name, version, scoring method, and generation timestamp</li>
                  <li>Optional hash proof must be complete before evidence is marked ready</li>
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  )
}
