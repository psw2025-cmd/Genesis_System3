import { useEffect, useMemo, useState } from 'react'
import { Activity, Bell, Menu, Search, Shield } from 'lucide-react'
import { useStore } from '../store'
import { fmt } from '../lib/utils'
import { brokerIsConnected, isNonAuthBrokerRejection } from '../lib/healthTruth'
import { resolveFeedQuality } from '../lib/feedQuality'
import { DASHBOARD_TABS } from './Sidebar'

function Clock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata', hour12: false,
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    }))
    tick()
    const timer = window.setInterval(tick, 1000)
    return () => window.clearInterval(timer)
  }, [])
  return <span className="num" style={{ color: 'var(--text-sec)', fontSize: 11 }}>{time} IST</span>
}

function MarketTicker({ label, spot, chg, marketOpen, missingLabel }: { label: string; spot?: number; chg?: number | null; marketOpen: boolean; missingLabel?: string }) {
  const up = (chg ?? 0) >= 0
  const missing = !spot
  const missingText = missingLabel || (marketOpen ? 'Warming' : 'After hours')
  return (
    <div className="hide-phone" style={{ minWidth: 88, padding: '0 10px', borderLeft: '1px solid var(--border)' }} title={missing ? missingText : undefined}>
      <div style={{ fontSize: 10, color: 'var(--text-mut)', letterSpacing: '0.02em' }}>{label}</div>
      <div className="num" style={{ marginTop: 2, fontSize: 13, lineHeight: 1.1, fontWeight: 700, color: 'var(--text-pri)' }}>
        {missing ? '—' : fmt(spot, 2)}
      </div>
      <div className="num" style={{ marginTop: 2, fontSize: 10, color: missing ? 'var(--amber)' : chg == null ? 'var(--text-mut)' : up ? 'var(--up)' : 'var(--down)' }}>
        {missing ? missingText : chg == null ? '—' : `${up ? '+' : ''}${chg.toFixed(2)}%`}
      </div>
    </div>
  )
}

function brokerError(obj: any) {
  if (!obj) return false
  const raw = obj.raw ?? obj.data ?? obj.normalized?.raw ?? obj.funds?.raw ?? obj
  const status = String(raw?.status ?? obj?.status ?? '').toLowerCase()
  const detail = JSON.stringify(raw?.remarks ?? raw?.error ?? obj?.error ?? obj?.message ?? '').toLowerCase()
  return status === 'failure' || detail.includes('invalid') || detail.includes('unauthorized') || detail.includes('token')
}

export function TopBar() {
  const {
    wsStatus, brokerConnected, marketOpen, setActiveTab, gainRank, chain,
    brokerStatus, brokerFunds, brokerHoldings, brokerPositions, apiStatus, health,
    alerts, sidebarOpen, setSidebarOpen, commandQuery, setCommandQuery, state, liveBoard,
  } = useStore()
  const [searchOpen, setSearchOpen] = useState(false)

  const boardSpot = (symbol: string) => {
    const row = (liveBoard?.indices || []).find((item: any) => String(item?.symbol || '').toUpperCase() === symbol)
    if (Number(row?.ltp) > 0) {
      return { spot: Number(row.ltp), chg: row?.change_pct == null ? null : Number(row.change_pct), rowFound: true }
    }
    return { spot: undefined as number | undefined, chg: null as number | null, rowFound: Boolean(row) }
  }

  const getSpot = (symbol: string) => {
    const fromBoard = boardSpot(symbol)
    if (fromBoard.spot) return fromBoard
    const row = chain?.[symbol]
    if (Number(row?.spot) > 0) {
      const rawChange = row?.change_pct ?? row?.pct_change ?? row?.spot_change_pct
      return { spot: Number(row.spot), chg: rawChange == null ? null : Number(rawChange), rowFound: fromBoard.rowFound }
    }
    const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
    const match = rankings.find((item: any) => String(item?.underlying ?? '').toUpperCase() === symbol)
    return Number(match?.spot_price) > 0
      ? { spot: Number(match.spot_price), chg: match?.change_pct == null ? null : Number(match.change_pct), rowFound: fromBoard.rowFound }
      : { spot: undefined, chg: null, rowFound: fromBoard.rowFound }
  }

  const nifty = getSpot('NIFTY')
  const bank = getSpot('BANKNIFTY')
  const fin = getSpot('FINNIFTY')
  const vix = getSpot('INDIAVIX')
  const mid = getSpot('MIDCPNIFTY')
  const liveBoardOk = Boolean(liveBoard?.success || (liveBoard?.live_count ?? 0) > 0)
  const vixMissingLabel = vix.spot
    ? undefined
    : vix.rowFound
      ? 'Dhan no quote'
      : liveBoardOk
        ? 'Dhan unavailable'
        : marketOpen
          ? 'Feed warming'
          : 'After-hours n/a'
  const hasError = apiStatus?.status === 'API_AUTH_REQUIRED'
    || brokerError(brokerStatus) || brokerError(brokerFunds) || brokerError(brokerHoldings) || brokerError(brokerPositions)
  const brokerGood = brokerIsConnected(health, brokerConnected, brokerStatus)
  const requestRejected = isNonAuthBrokerRejection(brokerStatus)
  const brokerLabel = requestRejected
    ? 'Request rejected'
    : (brokerConnected || brokerGood)
      ? 'Session OK'
      : hasError
        ? 'Auth issue'
        : 'Waiting'
  const brokerTone = requestRejected
    ? 'var(--amber)'
    : brokerConnected || brokerGood
      ? 'var(--up)'
      : hasError
        ? 'var(--down)'
        : 'var(--amber)'
  const liveOn = Boolean(state?.live_trading_enabled ?? health?.live_allowed)
  const tickAge = state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec
  const feed = resolveFeedQuality({
    marketOpen,
    wsStatus,
    tickAgeSec: tickAge,
    dataSource: state?.data_source || health?.data_source,
    brokerConnected: brokerConnected || brokerGood,
  })
  const alertCount = Array.isArray(alerts) ? alerts.length : 0
  const matches = useMemo(() => {
    const q = commandQuery.trim().toLowerCase()
    if (!q) return []
    return DASHBOARD_TABS.filter((tab) => tab.label.toLowerCase().includes(q) || tab.id.includes(q)).slice(0, 8)
  }, [commandQuery])

  useEffect(() => {
    const onKey = (ev: KeyboardEvent) => {
      if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') {
        ev.preventDefault()
        setSearchOpen(true)
        document.getElementById('dashboard-command')?.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <header role="banner" className="app-topbar">
      <div className="topbar-brand">
        <div aria-hidden className="topbar-mark">S</div>
        <div style={{ minWidth: 0 }}>
          <div className="topbar-title">SYSTEM3</div>
          <div className="topbar-subtitle">Genesis</div>
        </div>
        <button
          type="button"
          className="soft-btn"
          aria-label={sidebarOpen ? 'Close navigation' : 'Open navigation'}
          aria-expanded={sidebarOpen}
          aria-controls="dashboard-sidebar"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          style={{ marginLeft: 'auto', width: 28, minHeight: 28, padding: 0 }}
        >
          <Menu size={14} />
        </button>
      </div>

      <div className="topbar-status-strip" aria-label="Session status">
        <div className="status-item">
          <span className={`status-dot-quiet ${marketOpen ? 'tone-ok' : 'tone-warn'}`} aria-hidden />
          <div>
            <div className="status-label">{marketOpen ? 'Market open' : 'Market closed'}</div>
            <div className="status-sub">{marketOpen ? 'Session active' : 'Read-only / poll'}</div>
          </div>
        </div>

        <div className="status-item hide-phone" title={feed.detail}>
          <span className={`feed-badge feed-badge-${feed.tone}`}>{feed.label}</span>
          <div className="status-sub" style={{ marginLeft: 2 }}>{feed.detail}</div>
        </div>

        <div className="hide-compact" style={{ display: 'flex', alignItems: 'center' }}>
          <MarketTicker label="Nifty 50" spot={nifty.spot} chg={nifty.chg} marketOpen={marketOpen} />
          <MarketTicker label="Bank Nifty" spot={bank.spot} chg={bank.chg} marketOpen={marketOpen} />
          <MarketTicker label="Fin Nifty" spot={fin.spot} chg={fin.chg} marketOpen={marketOpen} />
          <MarketTicker label="India VIX" spot={vix.spot} chg={vix.chg} marketOpen={marketOpen} missingLabel={vixMissingLabel} />
          <MarketTicker label="Midcap" spot={mid.spot} chg={mid.chg} marketOpen={marketOpen} />
          <div className="hide-phone" style={{ minWidth: 54, padding: '0 8px', borderLeft: '1px solid var(--border)' }}>
            <div style={{ fontSize: 10, color: 'var(--text-mut)' }}>Board</div>
            <div className="num" style={{ marginTop: 2, fontSize: 11, fontWeight: 700, color: liveBoardOk ? 'var(--up)' : 'var(--amber)' }}>
              {liveBoardOk ? 'Live' : marketOpen ? 'Warming' : 'Idle'}
            </div>
          </div>
        </div>
      </div>

      <div className="topbar-actions">
        <div className="hide-compact" style={{ padding: '0 10px', textAlign: 'right' }}>
          <Clock />
        </div>

        <button
          type="button"
          aria-label={`Broker ${brokerLabel}`}
          onClick={() => setActiveTab('broker')}
          className="topbar-broker-btn"
          title={apiStatus?.message || 'Open broker'}
          style={{ color: brokerTone }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 10, color: 'var(--text-mut)' }}>
            <Shield size={12} aria-hidden /> Broker
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, marginTop: 2 }}>Dhan · {brokerLabel}</div>
        </button>

        <div className="mode-pair" aria-label="Trading mode">
          <span className="mode-chip mode-paper">Paper</span>
          <span className={`mode-chip ${liveOn ? 'mode-live-on' : 'mode-live-off'}`}>
            {liveOn ? 'Live on' : 'Live off'}
          </span>
        </div>

        <button
          type="button"
          className="soft-btn hide-phone"
          aria-label="Open system health"
          title="System health / data integrity"
          onClick={() => setActiveTab('data-integrity')}
          style={{ width: 'auto', minHeight: 30, padding: '0 10px', gap: 6, marginRight: 4 }}
        >
          <Activity size={13} aria-hidden />
          <span style={{ fontSize: 11 }}>System health</span>
        </button>

        <div className="hide-compact" style={{ width: 168, marginRight: 8, position: 'relative' }}>
          <Search size={13} style={{ position: 'absolute', left: 10, top: 9, color: 'var(--text-mut)' }} aria-hidden />
          <input
            id="dashboard-command"
            type="search"
            aria-label="Search dashboard tabs"
            placeholder="Search (Ctrl+K)"
            value={commandQuery}
            onChange={(e) => { setCommandQuery(e.target.value); setSearchOpen(true) }}
            onFocus={() => setSearchOpen(true)}
            onBlur={() => window.setTimeout(() => setSearchOpen(false), 150)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && matches[0]) {
                setActiveTab(matches[0].id)
                setCommandQuery('')
                setSearchOpen(false)
              }
            }}
            className="topbar-search"
          />
          {searchOpen && matches.length > 0 && (
            <ul role="listbox" aria-label="Matching tabs" className="topbar-search-menu">
              {matches.map((tab) => (
                <li key={tab.id}>
                  <button type="button" className="nav-item" onMouseDown={(e) => e.preventDefault()} onClick={() => { setActiveTab(tab.id); setCommandQuery(''); setSearchOpen(false) }}>
                    {tab.label}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <button type="button" className="soft-btn" aria-label={alertCount ? `${alertCount} alerts` : 'No active alerts'} onClick={() => setActiveTab('alerts')} style={{ width: 30, minHeight: 30, padding: 0, marginRight: 10, position: 'relative' }}>
          <Bell size={14} aria-hidden />
          {alertCount > 0 && (
            <span aria-hidden style={{ position: 'absolute', top: -4, right: -3, minWidth: 14, height: 14, display: 'grid', placeItems: 'center', borderRadius: 99, background: 'var(--down)', color: 'white', fontSize: 9, fontWeight: 800 }}>{alertCount}</span>
          )}
        </button>
      </div>
    </header>
  )
}
