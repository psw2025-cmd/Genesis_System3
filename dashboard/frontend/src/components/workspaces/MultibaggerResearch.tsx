import React, { useState, useEffect, useMemo } from 'react'
import { Sparkles, TrendingUp, Calendar, Target, ShieldCheck, Flame, RefreshCw, Layers } from 'lucide-react'
import { useStore } from '../../store'
import { API_HEADERS } from '../../config'
import { asFinite, formatInr, formatIstStamp } from '../../lib/formatLive'
import { resolveFeedQuality } from '../../lib/feedQuality'
import { brokerIsConnected } from '../../lib/healthTruth'
import { rankMultibagger } from '../../lib/sourceQuality'

type HorizonType = 'ALL' | 'WEEKLY' | 'MONTHLY' | 'YEARLY' | 'CORE'

export const MultibaggerResearch: React.FC = () => {
  const {
    research, state, health, paper, pnl, marketOpen, wsStatus, brokerConnected,
  } = useStore()
  
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [activeHorizon, setActiveHorizon] = useState<HorizonType>('ALL')

  const fetchMultibagger = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/multibagger', {
        credentials: 'include',
        headers: { Accept: 'application/json', ...API_HEADERS },
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      const ranked = rankMultibagger(json, useStore.getState().research)
      setData(ranked.value)
      if (Array.isArray(ranked.value?.candidates) && ranked.value.candidates.length > 0) {
        useStore.getState().setResearch(ranked.value)
      }
    } catch (err) {
      console.warn('Failed to fetch /api/multibagger:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMultibagger()
  }, [])

  const contract = data || research || {}
  const weeklyList: any[] = Array.isArray(contract.weekly) ? contract.weekly : []
  const monthlyList: any[] = Array.isArray(contract.monthly) ? contract.monthly : []
  const yearlyList: any[] = Array.isArray(contract.yearly) ? contract.yearly : []
  const coreList: any[] = Array.isArray(contract.candidates) ? contract.candidates : []

  // Combine all items into a unified list
  const allList = useMemo(() => {
    const combined: any[] = []
    weeklyList.forEach(item => combined.push({ ...item, horizon: item.horizon || 'WEEKLY' }))
    monthlyList.forEach(item => combined.push({ ...item, horizon: item.horizon || 'MONTHLY' }))
    yearlyList.forEach(item => combined.push({ ...item, horizon: item.horizon || 'YEARLY' }))
    coreList.forEach(item => {
      // Avoid duplicate symbols
      if (!combined.some(c => c.symbol === item.symbol)) {
        combined.push({ ...item, horizon: 'CORE' })
      }
    })
    return combined
  }, [weeklyList, monthlyList, yearlyList, coreList])

  const displayedCandidates = useMemo(() => {
    if (activeHorizon === 'WEEKLY') return weeklyList
    if (activeHorizon === 'MONTHLY') return monthlyList
    if (activeHorizon === 'YEARLY') return yearlyList
    if (activeHorizon === 'CORE') return coreList
    return allList
  }, [activeHorizon, weeklyList, monthlyList, yearlyList, coreList, allList])

  const totalCandidatesCount = allList.length || displayedCandidates.length

  const totalPnl = asFinite(paper?.pnl?.summary?.total_pnl) ?? asFinite(pnl?.summary?.total_pnl)
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

  const lastFetch = formatIstStamp(state?.last_fetch_ts_iso || contract.as_of)

  return (
    <div data-testid="multibagger-root" className="workspace-page">
      <header className="workspace-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
          <Sparkles size={20} color="var(--accent)" aria-hidden />
          <div>
            <h1 className="workspace-h1" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              Multibagger Research Engine
              <span style={{ fontSize: 11, background: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent)', padding: '2px 8px', borderRadius: 4, fontWeight: 700, border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                MULTI-HORIZON (1W TO 2Y)
              </span>
            </h1>
            <p className="workspace-lead">
              {totalCandidatesCount} research-universe names. Fundamentals/valuation are STATIC_RESEARCH_UNIVERSE; live price is overlaid when a Dhan/NSE quote exists. Not verified alpha. Not a LIVE order list.
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={fetchMultibagger}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--surface-3)',
              border: '1px solid var(--border)',
              borderRadius: 6,
              color: 'var(--text-pri)',
              padding: '6px 12px',
              fontSize: 12,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            {loading ? 'Scanning...' : 'Refresh Research'}
          </button>
          <span className={`feed-badge feed-badge-${feed.tone}`} title={feed.detail}>{feed.label}</span>
        </div>
      </header>

      <div className="workspace-body" style={{ padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Top Summary Hero Panel */}
        <section className="hero-panel" aria-label="Candidates summary">
          <div className="hero-main">
            <div className="metric-label">Research-universe names</div>
            <div className="hero-value num" data-testid="multibagger-candidate-count" style={{ color: 'var(--accent)' }}>
              {totalCandidatesCount}
            </div>
            <p className="hero-copy">
              Continuously screened via Stan Weinstein Stage-2 criteria, multi-year base breakouts, and delivery volume expansion.
            </p>
          </div>
          <div className="hero-metrics">
            <div className="metric-quiet">
              <div className="metric-label">Weekly Momentum</div>
              <div className="num metric-strong" style={{ color: '#38bdf8' }}>{weeklyList.length}</div>
              <div className="metric-hint">1-4 Weeks Horizon</div>
            </div>
            <div className="metric-quiet">
              <div className="metric-label">Monthly Stage-2</div>
              <div className="num metric-strong" style={{ color: '#10b981' }}>{monthlyList.length}</div>
              <div className="metric-hint">1-6 Months Horizon</div>
            </div>
            <div className="metric-quiet">
              <div className="metric-label">Yearly Compounders</div>
              <div className="num metric-strong" style={{ color: '#f59e0b' }}>{yearlyList.length}</div>
              <div className="metric-hint">6-24 Months Horizon</div>
            </div>
            <div className="metric-quiet">
              <div className="metric-label">Paper P&amp;L</div>
              <div className={`num metric-strong metric-${pnlTone}`}>
                {formatInr(totalPnl)}
              </div>
              <div className="metric-hint">Paper P&L (unproven vs LIVE)</div>
            </div>
          </div>
        </section>

        {/* Horizon Switcher Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, background: 'var(--surface-2)', padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {[
              { id: 'ALL', label: `All Candidates (${totalCandidatesCount})`, icon: Layers },
              { id: 'WEEKLY', label: `Weekly Momentum (${weeklyList.length})`, icon: Flame, color: '#38bdf8' },
              { id: 'MONTHLY', label: `Monthly Stage-2 (${monthlyList.length})`, icon: TrendingUp, color: '#10b981' },
              { id: 'YEARLY', label: `Yearly Macro (${yearlyList.length})`, icon: Target, color: '#f59e0b' },
              { id: 'CORE', label: `Core Research (${coreList.length})`, icon: ShieldCheck, color: 'var(--accent)' },
            ].map(({ id, label, icon: Icon, color }) => {
              const active = activeHorizon === id
              return (
                <button
                  key={id}
                  onClick={() => setActiveHorizon(id as HorizonType)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '6px 12px',
                    fontSize: 12,
                    fontWeight: active ? 700 : 500,
                    borderRadius: 6,
                    border: '1px solid',
                    borderColor: active ? (color || 'var(--accent)') : 'transparent',
                    background: active ? 'var(--surface-3)' : 'transparent',
                    color: active ? 'var(--text-pri)' : 'var(--text-sec)',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  <Icon size={14} color={color || 'var(--accent)'} />
                  {label}
                </button>
              )
            })}
          </div>
          <span style={{ fontSize: 12, color: 'var(--text-mut)' }}>
            Showing {displayedCandidates.length} candidate{displayedCandidates.length === 1 ? '' : 's'}
          </span>
        </div>

        {/* Candidates Table */}
        <section className="elevated-panel" style={{ padding: 20, overflowX: 'auto', background: 'var(--surface-2)', borderRadius: 8, border: '1px solid var(--border)' }}>
          <div style={{ marginBottom: 14 }}>
            <h2 className="section-title" style={{ fontSize: 16, margin: 0 }}>
              {activeHorizon === 'ALL' ? 'All Multi-Horizon Candidates' : `${activeHorizon} Horizon Research Board`}
            </h2>
            <p style={{ fontSize: 12, color: 'var(--text-sec)', margin: '4px 0 0' }}>
              Multi-factor fundamental screening, technical momentum breakout, delivery volume expansion, and catalysts.
            </p>
          </div>

          <table className="clean-table" style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-mut)', textAlign: 'left' }}>
                <th style={{ padding: '8px 10px' }}>Rank &amp; Symbol</th>
                <th style={{ padding: '8px 10px' }}>Horizon / Type</th>
                <th style={{ padding: '8px 10px', textAlign: 'right' }}>Current Px</th>
                <th style={{ padding: '8px 10px', textAlign: 'right' }}>Breakout / Entry</th>
                <th style={{ padding: '8px 10px', textAlign: 'right' }}>Target Px</th>
                <th style={{ padding: '8px 10px', textAlign: 'right' }}>Upside Potential</th>
                <th style={{ padding: '8px 10px', textAlign: 'right' }}>Stop Loss</th>
                <th style={{ padding: '8px 10px', textAlign: 'right' }}>Vol Exp (Del%)</th>
                <th style={{ padding: '8px 10px', textAlign: 'left' }}>Pattern / Thesis</th>
                <th style={{ padding: '8px 10px', textAlign: 'left' }}>Key Catalyst</th>
              </tr>
            </thead>
            <tbody>
              {displayedCandidates.map((row, idx) => {
                const upside = row.upside_potential_pct != null
                  ? `+${row.upside_potential_pct.toFixed(1)}%`
                  : row.target_potential || '—'
                const horizonLabel = row.horizon || row.timeframe || (row.thesis_status ? 'CORE' : 'WEEKLY')
                const currentPrice = row.current_price ?? row.price?.value ?? row.price
                const breakoutLevel = row.breakout_level ?? row.entry_price ?? row.technicals?.support_20d
                const targetPrice = row.target_price ?? (currentPrice && row.upside_potential_pct ? currentPrice * (1 + row.upside_potential_pct / 100) : null)
                const volRatio = row.volume_expansion_ratio ? `${row.volume_expansion_ratio}x` : '—'
                const delivPct = row.delivery_pct ? `(${row.delivery_pct}%)` : ''

                const horizonColor = horizonLabel === 'YEARLY'
                  ? '#f59e0b'
                  : horizonLabel === 'MONTHLY'
                    ? '#10b981'
                    : '#38bdf8'

                return (
                  <React.Fragment key={row.symbol || row.candidate_id || idx}>
                    <tr style={{ borderBottom: '1px solid var(--border)', transition: 'background 0.15s' }}>
                      <td style={{ padding: '10px 10px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontWeight: 700, color: 'var(--text-mut)', fontSize: 11, width: 18 }}>
                            #{row.rank ?? idx + 1}
                          </span>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-pri)' }}>
                              {row.symbol}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-mut)' }}>
                              {row.name || row.sector || ''}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '10px 10px' }}>
                        <span style={{
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '2px 7px',
                          borderRadius: 4,
                          background: `${horizonColor}18`,
                          color: horizonColor,
                          border: `1px solid ${horizonColor}40`,
                        }}>
                          {horizonLabel}
                        </span>
                        {row.timeframe && (
                          <div style={{ fontSize: 10, color: 'var(--text-mut)', marginTop: 2 }}>
                            {row.timeframe}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '10px 10px', textAlign: 'right', fontWeight: 700, color: 'var(--text-pri)' }}>
                        {formatInr(currentPrice)}
                      </td>
                      <td style={{ padding: '10px 10px', textAlign: 'right', color: 'var(--text-sec)' }}>
                        {breakoutLevel ? formatInr(breakoutLevel) : '—'}
                      </td>
                      <td style={{ padding: '10px 10px', textAlign: 'right', fontWeight: 700, color: '#10b981' }}>
                        {targetPrice ? formatInr(targetPrice) : '—'}
                      </td>
                      <td style={{ padding: '10px 10px', textAlign: 'right' }}>
                        <span style={{
                          fontSize: 12,
                          fontWeight: 700,
                          color: '#10b981',
                          background: 'rgba(16, 185, 129, 0.12)',
                          padding: '2px 6px',
                          borderRadius: 4,
                          border: '1px solid rgba(16, 185, 129, 0.25)',
                        }}>
                          {upside}
                        </span>
                      </td>
                      <td style={{ padding: '10px 10px', textAlign: 'right', color: '#ef4444', fontSize: 12 }}>
                        {row.stop_loss ? formatInr(row.stop_loss) : '—'}
                      </td>
                      <td style={{ padding: '10px 10px', textAlign: 'right', color: 'var(--text-pri)', fontSize: 12 }}>
                        {volRatio} <span style={{ fontSize: 10, color: 'var(--text-mut)' }}>{delivPct}</span>
                      </td>
                      <td style={{ padding: '10px 10px', fontSize: 12, color: 'var(--text-sec)', maxWidth: 220 }}>
                        {row.pattern || row.explain_why || row.thesis_status || 'Stage 2 Accumulation'}
                      </td>
                      <td style={{ padding: '10px 10px', fontSize: 11, color: 'var(--text-mut)', maxWidth: 240, lineHeight: 1.4 }}>
                        {row.catalyst || (Array.isArray(row.catalysts) ? row.catalysts.join(', ') : 'Earnings turnaround & expansion')}
                      </td>
                    </tr>
                  </React.Fragment>
                )
              })}
              {displayedCandidates.length === 0 && !loading && (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: 30, color: 'var(--text-mut)' }}>
                    No candidates found for {activeHorizon} horizon.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}
export default MultibaggerResearch
