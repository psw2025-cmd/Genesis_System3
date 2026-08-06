import { useStore } from './store'
import { useData } from './hooks/useData'

// ── Layout ────────────────────────────────────────────────────────────
import { TopBar }    from './components/TopBar'
import { Sidebar }   from './components/Sidebar'

// ── Tier A: Store-based tabs (no axios needed, data already streaming) ─
import { Overview }      from './components/Overview'
import { TradeTab }      from './components/TradeTab'
import { Positions }     from './components/Positions'
import { BrokerProofPanel } from './components/BrokerProofPanel'
import { OptionChain }   from './components/OptionChain'
import { AlertsTab }     from './components/AlertsTab'
import { SystemTab }     from './components/SystemTab'
import { LiveTradingGate } from './components/LiveTradingGate'
import { PerformanceTab }  from './components/PerformanceTab'
import { EndToEndProof }   from './components/EndToEndProof'
import { SystemTruthControl } from './components/SystemTruthControl'
import { LiveSimulation } from './components/LiveSimulation'

// ── Tier B: Axios-based tabs (need axios dep, call backend directly) ───
import Signals       from './components/Signals'
import PaperTrading  from './components/PaperTrading'
import MLPerformance from './components/MLPerformance'
import { GenesisTab } from './components/GenesisTab'

function ProductionProofBar() {
  const { autoGates, brokerConnected, paper, health } = useStore()
  const gatesObj = (autoGates?.gates && typeof autoGates.gates === 'object') ? autoGates.gates : {}
  const proofList = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const mlGate = gatesObj.ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS || proofList.find((g: any) => /spearman|ml accuracy/i.test(String(g?.label || g?.gate_id || '')))
  const profitGate = gatesObj.POSITIVE_NET_EXPECTANCY_AFTER_COSTS || proofList.find((g: any) => /expectancy|profit/i.test(String(g?.label || g?.gate_id || '')))
  const paperGate = gatesObj.REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF || proofList.find((g: any) => /paper lifecycle|provenance/i.test(String(g?.label || g?.gate_id || '')))
  const mlOk = Boolean(mlGate?.pass ?? mlGate?.ok)
  const profitOk = Boolean(profitGate?.pass ?? profitGate?.ok)
  const paperOk = Boolean(paperGate?.pass ?? paperGate?.ok)
  const mlLabel = mlOk
    ? `ρ=${mlGate?.latest_rho ?? 'ok'}`
    : `ML ${(mlGate?.days_recorded ?? 0)}/${(mlGate?.days_required ?? 5)}d`
  const paperLabel = paperOk
    ? 'PAPER OK'
    : (profitOk ? 'PROVENANCE' : `EXP ${profitGate?.net_expectancy_after_costs ?? paper?.summary?.avg_pnl_per_trade ?? '—'}`)
  const cloudUiOk = Boolean(brokerConnected || health?.broker_status === 'connected')
  const proofItems: Array<[string, string, boolean]> = [
    ['LIVE', 'OFF', true],
    ['MODE', 'PAPER', true],
    ['DATA', brokerConnected ? 'DHAN' : 'DHAN REQ', brokerConnected],
    ['ML', mlLabel, mlOk],
    ['PAPER', paperLabel, paperOk],
    ['UI', cloudUiOk ? 'LIVE' : 'CHECK', cloudUiOk],
  ]

  return (
    <div
      data-testid="production-proof-bar"
      aria-label="Production proof status"
      title="Proof status from /api/auto_gates + broker health"
      style={{
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 12px',
        minHeight: '36px',
        background: 'var(--surface-1)',
        borderBottom: '1px solid var(--border)',
        overflowX: 'auto',
      }}
    >
      <span style={{
        color: 'var(--text-mut)',
        fontSize: '10px',
        fontFamily: 'var(--font-mono)',
        fontWeight: 700,
        letterSpacing: '0.08em',
        whiteSpace: 'nowrap',
      }}>PROOF</span>
      {proofItems.map(([label, value, safe]) => (
        <div
          key={label}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '3px 8px',
            borderRadius: '6px',
            background: safe ? 'rgba(0,232,122,.08)' : 'rgba(245,158,11,.10)',
            border: safe ? '1px solid rgba(0,232,122,.28)' : '1px solid rgba(245,158,11,.28)',
            whiteSpace: 'nowrap',
          }}
        >
          <span style={{
            color: 'var(--text-mut)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            letterSpacing: '0.06em',
          }}>{label}</span>
          <span style={{
            color: safe ? 'var(--up)' : 'var(--amber)',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
          }}>{value}</span>
        </div>
      ))}
    </div>
  )
}

function Content() {
  const { activeTab } = useStore()
  switch (activeTab) {
    case 'truth':        return <SystemTruthControl />
    case 'overview':     return <Overview />
    case 'trade':        return <TradeTab />
    case 'positions':    return <Positions />
    case 'chain':        return <OptionChain />
    case 'signals':      return <Signals />
    case 'paper':        return <PaperTrading />
    case 'performance':  return <PerformanceTab />
    case 'ml':           return <MLPerformance />
    case 'genesis':      return <GenesisTab />
    case 'e2e-proof':    return <EndToEndProof />
    case 'broker':       return <BrokerProofPanel />
    case 'alerts':       return <AlertsTab />
    case 'system':       return <SystemTab />
    case 'gates':        return <LiveTradingGate />
    case 'sim-live':     return <LiveSimulation />
    default:             return <SystemTruthControl />
  }
}

export default function App() {
  useData()
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column',
                  background: 'var(--surface)', overflow: 'hidden' }}>
      <TopBar />
      <ProductionProofBar />
      <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, minWidth: 0, minHeight: 0, overflow: 'hidden' }}>
          <Content />
        </main>
      </div>
    </div>
  )
}
