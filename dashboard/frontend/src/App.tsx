import { useStore } from './store'
import { useData } from './hooks/useData'

// ── Layout ────────────────────────────────────────────────────────────
import { TopBar }    from './components/TopBar'
import { Sidebar }   from './components/Sidebar'

// ── Tier A: Store-based tabs (no axios needed, data already streaming) ─
import { Overview }      from './components/Overview'
import { TradeTab }      from './components/TradeTab'
import { Positions }     from './components/Positions'
import { BrokerPanel }   from './components/BrokerPanel'
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
    : `TRAINING ${(mlGate?.days_recorded ?? 0)}/${(mlGate?.days_required ?? 5)}d`
  const paperLabel = paperOk
    ? 'LIFECYCLE PROVEN'
    : (profitOk ? 'PROVENANCE PENDING' : `EXPECTANCY ${profitGate?.net_expectancy_after_costs ?? paper?.summary?.avg_pnl_per_trade ?? 'N/A'}`)
  const renderOk = Boolean(brokerConnected || health?.broker_status === 'connected')
  const proofItems: Array<[string, string, boolean]> = [
    ['OWNER', 'PRITAM S. WARGHADE', true],
    ['LIVE', 'OFF', true],
    ['MODE', 'PAPER ONLY', true],
    ['DATA', brokerConnected ? 'DHAN CONNECTED' : 'DHAN ONLY REQUIRED', brokerConnected],
    ['ML SCORE', mlLabel, mlOk],
    ['PAPER', paperLabel, paperOk],
    ['RENDER', renderOk ? 'BROKER UI LIVE' : 'VISUAL PROOF REQUIRED', renderOk],
  ]

  return (
    <div
      data-testid="production-proof-bar"
      aria-label="Production proof bar for Pritam S. Warghade"
      style={{
        position: 'fixed',
        left: '12px',
        right: '12px',
        bottom: '12px',
        zIndex: 9999,
        pointerEvents: 'none',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(128px, 1fr))',
        gap: '6px',
        padding: '8px',
        borderRadius: '16px',
        background: 'linear-gradient(135deg, rgba(2,6,23,.94), rgba(15,23,42,.88))',
        border: '1px solid rgba(59,130,246,.40)',
        boxShadow: '0 0 28px rgba(59,130,246,.20), inset 0 0 18px rgba(0,232,122,.08)',
        backdropFilter: 'blur(10px)',
      }}
      title="Production-grade proof bar — values come from /api/auto_gates + broker health"
    >
      {proofItems.map(([label, value, safe]) => (
        <div key={label} style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '2px',
          minWidth: 0,
          padding: '6px 8px',
          borderRadius: '10px',
          background: safe ? 'rgba(0,232,122,.08)' : 'rgba(245,158,11,.10)',
          border: safe ? '1px solid rgba(0,232,122,.26)' : '1px solid rgba(245,158,11,.30)',
        }}>
          <span style={{
            color: 'var(--text-mut)',
            fontSize: '.48rem',
            lineHeight: 1,
            fontFamily: 'var(--font-mono)',
            letterSpacing: '.18em',
            fontWeight: 900,
            whiteSpace: 'nowrap',
          }}>{label}</span>
          <span style={{
            color: safe ? 'var(--accent)' : 'var(--amber)',
            fontSize: '.62rem',
            lineHeight: 1.1,
            fontWeight: 950,
            letterSpacing: '.06em',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
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
    case 'broker':       return <BrokerPanel />
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
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', paddingBottom: '76px' }}>
        <Sidebar />
        <main style={{ flex: 1, overflow: 'hidden' }}>
          <Content />
        </main>
      </div>
    </div>
  )
}
