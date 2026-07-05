import { useState, useEffect } from 'react'
import { useStore } from '../store'
import { fmt } from '../lib/utils'

function Clock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata', hour12: false,
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    }))
    tick(); const t = setInterval(tick, 1000); return () => clearInterval(t)
  }, [])
  return <span className="num" style={{ color:'var(--accent)', fontSize:'1rem', fontWeight:600, letterSpacing:'.05em' }}>{time} IST</span>
}

function IndexChip({ symbol, spot, chg }: { symbol:string; spot?:number; chg?:number }) {
  const isUp = (chg ?? 0) >= 0
  return (
    <div style={{ display:'flex', alignItems:'center', gap:'5px', padding:'3px 10px',
                  background:'var(--surface-2)', borderRadius:'6px', border:'1px solid var(--border)' }}>
      <span style={{ fontSize:'.6rem', color:'var(--text-mut)', fontFamily:'var(--font-mono)', fontWeight:700 }}>{symbol}</span>
      <span className="num" style={{ fontSize:'.8rem', fontWeight:700, color:'var(--text-pri)' }}>
        {spot ? fmt(spot, 0) : '--'}
      </span>
      {chg != null && spot && (
        <span className="num" style={{ fontSize:'.55rem', color: isUp ? 'var(--up)' : 'var(--down)' }}>
          {isUp ? '▲' : '▼'}{Math.abs(chg).toFixed(1)}%
        </span>
      )}
    </div>
  )
}

export function TopBar() {
  const { wsStatus, brokerConnected, marketOpen, setActiveTab, gainRank, state, chain } = useStore()
  const rho = state?.signals?.spearman_rho ?? null

  // Spot prices come from gain_rank.latest.rankings — this is the ONLY endpoint
  // that returns actual spot_price per underlying. /api/underlyings only returns
  // a bare name list (["NIFTY","BANKNIFTY",...]) with no price data — never use it
  // for spot prices. gain_rank is file-based and persists across market hours,
  // so this also satisfies "show last known data when market is closed".
  const getSpot = (sym: string) => {
    // Handle multiple data shapes from gain_rank API:
    // Shape 1: {latest: {rankings: [{underlying, spot_price, change_pct}]}}
    // Shape 2: {rankings: [{underlying, spot_price}]}
    // Shape 3 (actual): [{date, predictions: [{underlying, gain_score}]}]
    // Also try chain data for live spot when market open
    const chainData = chain[sym]
    if (chainData?.spot && chainData.spot > 0) {
      return { spot: chainData.spot, chg: null }
    }
    const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
    const entry = rankings.find((r: any) => r.underlying === sym)
    if (entry?.spot_price) return { spot: entry.spot_price, chg: entry.change_pct ?? null }
    return null
  }

  const nifty    = getSpot('NIFTY')
  const bnfty    = getSpot('BANKNIFTY')
  const finnifty = getSpot('FINNIFTY')

  return (
    <header style={{
      height:'52px', background:'var(--surface-1)', borderBottom:'1px solid var(--border)',
      display:'flex', alignItems:'center', padding:'0 12px', gap:'10px',
      flexShrink:0, zIndex:50, overflow:'hidden'
    }}>
      <div style={{ display:'flex', alignItems:'center', gap:'6px', flexShrink:0 }}>
        <span style={{ color:'var(--accent)', fontWeight:800, fontSize:'.8rem', letterSpacing:'.1em' }}>SYSTEM3</span>
        <span style={{ color:'var(--text-mut)', fontSize:'.6rem' }}>PSW</span>
      </div>
      <div style={{ width:'1px', height:'28px', background:'var(--border)' }} />
      <Clock />
      <div style={{ width:'1px', height:'28px', background:'var(--border)' }} />

      <div style={{ display:'flex', gap:'6px', flex:1, overflow:'hidden' }}>
        <IndexChip symbol="NIFTY"    spot={nifty?.spot}    chg={nifty?.chg ?? undefined} />
        <IndexChip symbol="BNFTY"    spot={bnfty?.spot}    chg={bnfty?.chg ?? undefined} />
        <IndexChip symbol="FINNIFTY" spot={finnifty?.spot} chg={finnifty?.chg ?? undefined} />
      </div>

      <div style={{ display:'flex', alignItems:'center', gap:'5px', flexShrink:0 }}>
        <span style={{
          display:'inline-flex', alignItems:'center', gap:'4px', padding:'3px 8px',
          borderRadius:'6px', fontSize:'.62rem', fontWeight:700, fontFamily:'var(--font-mono)',
          background: marketOpen ? 'rgba(0,232,122,.1)' : 'rgba(255,77,106,.08)',
          color: marketOpen ? 'var(--up)' : 'var(--down)',
          border:`1px solid ${marketOpen ? 'rgba(0,232,122,.25)' : 'rgba(255,77,106,.2)'}`,
        }}>
          <span style={{ width:'6px', height:'6px', borderRadius:'50%',
                         background: marketOpen ? 'var(--up)' : 'var(--down)',
                         animation: marketOpen ? 'pulseDot 1.5s infinite' : 'none' }} />
          {marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}
        </span>

        <span onClick={() => setActiveTab('broker')} style={{
          display:'inline-flex', alignItems:'center', gap:'4px', padding:'3px 8px',
          borderRadius:'6px', fontSize:'.62rem', fontWeight:700, fontFamily:'var(--font-mono)', cursor:'pointer',
          background: brokerConnected ? 'rgba(0,232,122,.1)' : 'rgba(255,77,106,.08)',
          color: brokerConnected ? 'var(--up)' : 'var(--down)',
          border:`1px solid ${brokerConnected ? 'rgba(0,232,122,.25)' : 'rgba(255,77,106,.2)'}`,
        }} title="Click → Broker Data">
          <span style={{ width:'6px', height:'6px', borderRadius:'50%',
                         background: brokerConnected ? 'var(--up)' : 'var(--down)' }} />
          DHAN {brokerConnected ? '✓' : '✗'}
        </span>

        <span style={{ padding:'3px 8px', borderRadius:'6px', fontSize:'.62rem', fontWeight:700,
                       background:'rgba(245,158,11,.1)', color:'var(--amber)',
                       border:'1px solid rgba(245,158,11,.25)', fontFamily:'var(--font-mono)' }}>PAPER</span>

        <span style={{ padding:'3px 8px', borderRadius:'6px', fontSize:'.62rem', fontWeight:700,
                       background:'rgba(255,77,106,.06)', color:'var(--down)',
                       border:'1px solid rgba(255,77,106,.18)', fontFamily:'var(--font-mono)' }}>LIVE OFF</span>

        <div style={{ display:'flex', alignItems:'center', gap:'4px', padding:'3px 7px',
                      background:'var(--surface-2)', borderRadius:'5px', border:'1px solid var(--border)' }}
             title={`WebSocket: ${wsStatus}`}>
          <span style={{
            width:'6px', height:'6px', borderRadius:'50%',
            background: wsStatus==='live' ? 'var(--up)' : wsStatus==='connecting' ? 'var(--amber)' : 'var(--down)',
            animation: wsStatus==='live' ? 'pulseDot 1.5s infinite' : 'none'
          }} />
          <span style={{ fontSize:'.55rem', fontFamily:'var(--font-mono)', color:'var(--text-mut)' }}>WS</span>
          <span style={{ fontSize:'.55rem', fontFamily:'var(--font-mono)',
                         color: wsStatus==='live' ? 'var(--up)' : 'var(--text-mut)' }}>
            {wsStatus === 'live' ? 'LIVE' : wsStatus === 'connecting' ? 'CONNECTING' : 'OFF'}
          </span>
        </div>

        {rho != null && (
          <div style={{ padding:'3px 7px', background:'var(--surface-2)',
                        borderRadius:'5px', border:'1px solid var(--border)' }}>
            <span style={{ fontSize:'.55rem', color:'var(--text-mut)', fontFamily:'var(--font-mono)' }}>ρ </span>
            <span className="num" style={{ fontSize:'.75rem', fontWeight:700,
                                           color: rho>=0.7 ? 'var(--up)' : rho>=0.4 ? 'var(--amber)' : 'var(--down)' }}>
              {rho.toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </header>
  )
}
