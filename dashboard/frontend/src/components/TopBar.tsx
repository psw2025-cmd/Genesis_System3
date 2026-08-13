import { useEffect, useState } from 'react'
import { Bell, ChevronDown, Menu, Search, Shield, Wifi } from 'lucide-react'
import { useStore } from '../store'
import { fmt } from '../lib/utils'

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
  return <span className="num" style={{ color: 'var(--text-sec)', fontSize: '.58rem' }}>{time} IST</span>
}

function MarketTicker({ label, spot, chg }: { label: string; spot?: number; chg?: number | null }) {
  const up = (chg ?? 0) >= 0
  return (
    <div style={{ minWidth: 94, padding: '0 11px', borderLeft: '1px solid var(--border)' }}>
      <div className="metric-label" style={{ fontSize: '.52rem' }}>{label}</div>
      <div className="num" style={{ marginTop: 2, fontSize: '.72rem', lineHeight: 1.05, fontWeight: 800, color: 'var(--text-pri)' }}>
        {spot ? fmt(spot, 2) : '--'}
      </div>
      <div className="num" style={{ marginTop: 2, fontSize: '.52rem', color: chg == null ? 'var(--text-mut)' : up ? 'var(--up)' : 'var(--down)' }}>
        {chg == null ? 'WAITING' : `${up ? '+' : ''}${chg.toFixed(2)}%`}
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
    brokerStatus, brokerFunds, brokerHoldings, brokerPositions, apiStatus,
  } = useStore()

  const getSpot = (symbol: string) => {
    const row = chain?.[symbol]
    if (Number(row?.spot) > 0) {
      const rawChange = row?.change_pct ?? row?.pct_change ?? row?.spot_change_pct
      return { spot: Number(row.spot), chg: rawChange == null ? null : Number(rawChange) }
    }
    const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
    const match = rankings.find((item: any) => String(item?.underlying ?? '').toUpperCase() === symbol)
    return Number(match?.spot_price) > 0
      ? { spot: Number(match.spot_price), chg: match?.change_pct == null ? null : Number(match.change_pct) }
      : { spot: undefined, chg: null }
  }

  const nifty = getSpot('NIFTY')
  const bank = getSpot('BANKNIFTY')
  const mid = getSpot('MIDCPNIFTY')
  const apiResponded = Boolean(brokerStatus || brokerFunds || brokerHoldings || brokerPositions)
  const hasError = apiStatus?.status === 'API_AUTH_REQUIRED'
    || brokerError(brokerStatus) || brokerError(brokerFunds) || brokerError(brokerHoldings) || brokerError(brokerPositions)
  const brokerGood = brokerConnected || (apiResponded && !hasError)
  const brokerTone = brokerGood ? 'var(--up)' : hasError ? 'var(--down)' : 'var(--amber)'
  const brokerLabel = brokerConnected ? 'CONNECTED' : brokerGood ? 'API OK' : hasError ? 'AUTH ISSUE' : 'WAITING'
  const marketTone = marketOpen ? 'var(--up)' : 'var(--amber)'
  const wsTone = wsStatus === 'live' ? 'var(--up)' : wsStatus === 'connecting' ? 'var(--amber)' : 'var(--down)'

  return (
    <header style={{
      height: 58,
      flexShrink: 0,
      display: 'flex',
      alignItems: 'stretch',
      background: 'linear-gradient(180deg, rgba(7,18,31,.98), rgba(5,14,25,.98))',
      borderBottom: '1px solid var(--border)',
      boxShadow: '0 8px 24px rgba(0,0,0,.18)',
      zIndex: 40,
      overflow: 'hidden',
    }}>
      <div style={{ width: 168, flexShrink: 0, padding: '0 12px', display: 'flex', alignItems: 'center', gap: 10, borderRight: '1px solid var(--border)' }}>
        <div aria-hidden style={{ width: 25, height: 25, borderRadius: 8, display: 'grid', placeItems: 'center', color: 'var(--accent)', border: '1px solid rgba(59,140,255,.4)', background: 'rgba(59,140,255,.1)', fontWeight: 900 }}>S</div>
        <div style={{ minWidth: 0 }}>
          <div style={{ color: '#63a7ff', fontWeight: 900, fontSize: '.76rem', letterSpacing: '.18em', lineHeight: 1 }}>SYSTEM3</div>
          <div style={{ color: 'var(--text-mut)', fontSize: '.48rem', letterSpacing: '.2em', marginTop: 4 }}>GENESIS</div>
        </div>
        <button className="soft-btn" aria-label="Menu" style={{ marginLeft: 'auto', width: 28, minHeight: 28, padding: 0 }}><Menu size={14} /></button>
      </div>

      <div className="top-chip" style={{ border: 0, borderRadius: 0, background: 'transparent', minWidth: 128, paddingInline: 14 }}>
        <span className="status-dot" style={{ color: marketTone }} />
        <div>
          <div style={{ color: marketTone, fontSize: '.58rem', fontWeight: 900 }}>{marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}</div>
          <div style={{ color: 'var(--text-mut)', fontSize: '.48rem', marginTop: 2 }}>{marketOpen ? 'LIVE DATA' : 'READ-ONLY / POLL'}</div>
        </div>
      </div>

      <div className="hide-compact" style={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
        <MarketTicker label="NIFTY" spot={nifty.spot} chg={nifty.chg} />
        <MarketTicker label="BANKNIFTY" spot={bank.spot} chg={bank.chg} />
        <MarketTicker label="MIDCPNIFTY" spot={mid.spot} chg={mid.chg} />
      </div>

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', minWidth: 0 }}>
        <div className="hide-compact" style={{ padding: '0 11px', borderLeft: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: wsTone }}>
            <Wifi size={13} />
            <span style={{ fontSize: '.55rem', fontWeight: 800 }}>WS {wsStatus === 'live' ? 'LIVE' : wsStatus.toUpperCase()}</span>
          </div>
          <Clock />
        </div>

        <button onClick={() => setActiveTab('broker')} style={{
          height: '100%', minWidth: 108, padding: '0 12px', border: 0, borderLeft: '1px solid var(--border)', borderRight: '1px solid var(--border)',
          background: 'transparent', color: brokerTone, cursor: 'pointer', textAlign: 'left',
        }} title={apiStatus?.message || 'Open Broker'}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '.53rem', color: 'var(--text-mut)' }}><Shield size={12} /> BROKER</div>
          <div style={{ fontSize: '.61rem', fontWeight: 900, marginTop: 3 }}>DHAN · {brokerLabel}</div>
        </button>

        <div style={{ padding: '0 10px', display: 'flex', gap: 5, alignItems: 'center' }}>
          <span className="pill" style={{ color: 'var(--amber)', border: '1px solid rgba(245,165,36,.28)', background: 'rgba(245,165,36,.08)' }}>PAPER</span>
          <span className="pill" style={{ color: 'var(--down)', border: '1px solid rgba(255,73,100,.24)', background: 'rgba(255,73,100,.06)' }}>LIVE OFF</span>
        </div>

        <div className="hide-compact" style={{ width: 184, marginRight: 10, position: 'relative' }}>
          <Search size={13} style={{ position: 'absolute', left: 10, top: 9, color: 'var(--text-mut)' }} />
          <div style={{ height: 31, display: 'flex', alignItems: 'center', paddingLeft: 31, color: 'var(--text-mut)', border: '1px solid var(--border)', borderRadius: 7, fontSize: '.58rem', background: 'rgba(6,16,28,.75)' }}>
            Search (Ctrl + K)
          </div>
        </div>

        <button className="soft-btn" aria-label="Notifications" style={{ width: 30, minHeight: 30, padding: 0, marginRight: 8, position: 'relative' }}>
          <Bell size={14} />
          <span style={{ position: 'absolute', top: -4, right: -3, minWidth: 14, height: 14, display: 'grid', placeItems: 'center', borderRadius: 99, background: 'var(--down)', color: 'white', fontSize: '.45rem', fontWeight: 900 }}>!</span>
        </button>

        <div style={{ paddingRight: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 28, height: 28, borderRadius: 99, display: 'grid', placeItems: 'center', background: 'var(--surface-3)', border: '1px solid var(--border-hi)', color: 'var(--text-pri)', fontSize: '.58rem', fontWeight: 800 }}>PS</div>
          <div className="hide-compact" style={{ lineHeight: 1.1 }}>
            <div style={{ color: 'var(--text-pri)', fontSize: '.58rem', fontWeight: 750 }}>Pritam S.</div>
            <div style={{ color: 'var(--text-mut)', fontSize: '.48rem', marginTop: 3 }}>Admin</div>
          </div>
          <ChevronDown className="hide-compact" size={12} color="var(--text-mut)" />
        </div>
      </div>
    </header>
  )
}
