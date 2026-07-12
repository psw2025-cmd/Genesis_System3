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

// ── Tier B: Axios-based tabs (need axios dep, call backend directly) ───
import Signals       from './components/Signals'
import PaperTrading  from './components/PaperTrading'
import MLPerformance from './components/MLPerformance'
import { GenesisTab } from './components/GenesisTab'

function OwnerVisualBadge() {
  return (
    <div
      data-testid="owner-visual-badge"
      aria-label="System owner Pritam S. Warghade"
      style={{
        position: 'fixed',
        right: '12px',
        bottom: '12px',
        zIndex: 9999,
        pointerEvents: 'none',
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
        padding: '8px 12px',
        borderRadius: '14px',
        background: 'linear-gradient(135deg, rgba(2,6,23,.92), rgba(15,23,42,.86))',
        border: '1px solid rgba(0,232,122,.45)',
        boxShadow: '0 0 26px rgba(0,232,122,.22), inset 0 0 18px rgba(59,130,246,.10)',
        backdropFilter: 'blur(8px)',
        maxWidth: 'calc(100vw - 24px)',
      }}
      title="OWNER / PRITAM S. WARGHADE — required dashboard visual proof"
    >
      <span style={{
        color: 'var(--text-mut)',
        fontSize: '.52rem',
        lineHeight: 1,
        fontFamily: 'var(--font-mono)',
        letterSpacing: '.22em',
        fontWeight: 800,
      }}>OWNER / OPERATOR</span>
      <span style={{
        color: 'var(--accent)',
        fontSize: '.78rem',
        lineHeight: 1.1,
        fontWeight: 950,
        letterSpacing: '.10em',
        whiteSpace: 'nowrap',
      }}>PRITAM S. WARGHADE</span>
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
    default:             return <SystemTruthControl />
  }
}

export default function App() {
  useData()
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column',
                  background: 'var(--surface)', overflow: 'hidden' }}>
      <TopBar />
      <OwnerVisualBadge />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, overflow: 'hidden' }}>
          <Content />
        </main>
      </div>
    </div>
  )
}
