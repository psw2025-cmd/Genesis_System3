import { useEffect, useMemo, useState } from 'react'
import { Activity, Bell, Menu, Search, Shield, Clock as ClockIcon } from 'lucide-react'
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
  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300 font-mono text-xs font-semibold shrink-0">
      <ClockIcon size={13} className="text-sky-400" />
      <span>{time || '00:00:00'} IST</span>
    </div>
  )
}

function MarketTicker({
  label,
  spot,
  chg,
  marketOpen,
  missingLabel
}: {
  label: string
  spot?: number
  chg?: number | null
  marketOpen: boolean
  missingLabel?: string
}) {
  const up = (chg ?? 0) >= 0
  const missing = !spot || spot <= 0
  const missingText = missingLabel || (marketOpen ? 'Warming' : 'After hours')

  return (
    <div className="flex flex-col justify-center px-3 py-1 border-l border-slate-800/80 min-w-[100px] shrink-0" title={missing ? missingText : undefined}>
      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{label}</div>
      <div className="font-mono text-sm font-bold text-slate-100 mt-0.5 tabular-nums">
        {missing ? '—' : fmt(spot, 2)}
      </div>
      <div className={`font-mono text-[11px] font-semibold mt-0.5 tabular-nums ${
        missing ? 'text-amber-400' : chg == null ? 'text-slate-400' : up ? 'text-emerald-400' : 'text-rose-400'
      }`}>
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

  const liveOn = Boolean(state?.live_trading_enabled ?? health?.live_allowed)
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
    <header role="banner" className="h-14 bg-slate-950 border-b border-slate-800 flex items-center justify-between px-3 md:px-4 z-40 shrink-0 gap-3">
      {/* Brand & Nav Toggle */}
      <div className="flex items-center gap-3 shrink-0">
        <button
          type="button"
          className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 active:scale-95 transition-all"
          aria-label={sidebarOpen ? 'Close navigation' : 'Open navigation'}
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          <Menu size={18} />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center font-extrabold text-blue-400 text-sm">
            S3
          </div>
          <div>
            <div className="text-sm font-extrabold tracking-wider text-slate-100 leading-none">SYSTEM3</div>
            <div className="text-[11px] font-semibold text-blue-400/90 leading-none mt-1">GENESIS INSTITUTIONAL</div>
          </div>
        </div>
      </div>

      {/* Market Tickers (Scrollable with no overlap) */}
      <div className="hidden lg:flex items-center overflow-x-auto scrollbar-none flex-1 max-w-2xl px-2">
        <MarketTicker label="Nifty 50" spot={nifty.spot} chg={nifty.chg} marketOpen={marketOpen} />
        <MarketTicker label="Bank Nifty" spot={bank.spot} chg={bank.chg} marketOpen={marketOpen} />
        <MarketTicker label="Fin Nifty" spot={fin.spot} chg={fin.chg} marketOpen={marketOpen} />
        <MarketTicker label="Midcap" spot={mid.spot} chg={mid.chg} marketOpen={marketOpen} />
        <MarketTicker label="India VIX" spot={vix.spot} chg={vix.chg} marketOpen={marketOpen} missingLabel={vixMissingLabel} />
        <div className="flex flex-col justify-center px-3 py-1 border-l border-slate-800/80 min-w-[70px] shrink-0">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Board</div>
          <div className={`font-mono text-xs font-bold mt-0.5 ${liveBoardOk ? 'text-emerald-400' : 'text-amber-400'}`}>
            {liveBoardOk ? (marketOpen ? 'Feed OK' : 'Snapshot') : marketOpen ? 'Warming' : 'Idle'}
          </div>
        </div>
      </div>

      {/* Right Actions & Telemetry */}
      <div className="flex items-center gap-2.5 shrink-0">
        <Clock />

        {/* Broker / System Health Button */}
        <button
          type="button"
          onClick={() => setActiveTab('broker')}
          className={`flex items-center gap-2 px-2.5 py-1 rounded-lg border text-xs font-semibold transition-all ${
            brokerConnected || brokerGood
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
              : 'bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20'
          }`}
          title="System health · Dhan status"
          aria-label="System health"
        >
          <Shield size={14} />
          <span>Dhan · {brokerLabel}</span>
        </button>

        {/* Paper / Live Mode Pill */}
        <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-semibold" title={liveOn ? 'Live on' : 'Live off'}>
          <span className="text-amber-400 font-bold">PAPER</span>
          <span className="text-slate-600">|</span>
          <span className={liveOn ? 'text-rose-400 font-bold' : 'text-slate-400'}>
            {liveOn ? 'Live on' : 'Live off'}
          </span>
        </div>

        {/* Quick Search */}
        <div className="hidden xl:block relative w-48">
          <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
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
            className="w-full h-8 pl-8 pr-3 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
          {searchOpen && matches.length > 0 && (
            <ul role="listbox" className="absolute top-9 left-0 right-0 bg-slate-900 border border-slate-700 rounded-lg shadow-xl py-1 z-50">
              {matches.map((tab) => (
                <li key={tab.id}>
                  <button
                    type="button"
                    className="w-full text-left px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 hover:text-blue-400 transition-colors"
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => { setActiveTab(tab.id); setCommandQuery(''); setSearchOpen(false) }}
                  >
                    {tab.label}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Alerts Bell */}
        <button
          type="button"
          className="relative p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
          aria-label={alertCount ? `${alertCount} alerts` : 'No active alerts'}
          onClick={() => setActiveTab('alerts')}
        >
          <Bell size={16} />
          {alertCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white rounded-full flex items-center justify-center text-[10px] font-bold">
              {alertCount}
            </span>
          )}
        </button>
      </div>
    </header>
  )
}
export default TopBar
