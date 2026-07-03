import { useStore } from './store'
import { useData } from './hooks/useData'

// ── Layout ────────────────────────────────────────────────────────────
import { TopBar }    from './components/TopBar'
import { Sidebar }   from './components/Sidebar'
import BackendConnectivityBanner from './components/BackendConnectivityBanner'

// ── Tier A: Store-based tabs (data streaming from useData) ────────────
import { Overview }        from './components/Overview'
import { TradeTab }        from './components/TradeTab'
import { Positions }       from './components/Positions'
import { BrokerPanel }     from './components/BrokerPanel'
import { OptionChain }     from './components/OptionChain'
import { AlertsTab }       from './components/AlertsTab'
import { SystemTab }       from './components/SystemTab'
import { LiveTradingGate } from './components/LiveTradingGate'
import { PerformanceTab }  from './components/PerformanceTab'

// ── Tier B: Axios-based tabs ──────────────────────────────────────────
import Signals        from './components/Signals'
import PaperTrading   from './components/PaperTrading'
import MLPerformance  from './components/MLPerformance'
import RiskDashboard  from './components/RiskDashboard'
import ChainAnalytics from './components/ChainAnalytics'
import AdvancedCharts from './components/AdvancedCharts'
import Backtest       from './components/Backtest'
import ControlPlane   from './components/ControlPlane'
import ModelBehavior  from './components/ModelBehavior'
import AgentConsole   from './components/AgentConsole'
import AppSelfTest    from './components/AppSelfTest'

function Content() {
  const { activeTab } = useStore()
  switch (activeTab) {
    case 'overview':     return <Overview />
    case 'trade':        return <TradeTab />
    case 'positions':    return <Positions />
    case 'chain':        return <OptionChain />
    case 'analytics':    return <ChainAnalytics />
    case 'signals':      return <Signals />
    case 'paper':        return <PaperTrading />
    case 'performance':  return <PerformanceTab />
    case 'ml':           return <MLPerformance />
    case 'risk':         return <RiskDashboard />
    case 'charts':       return <AdvancedCharts />
    case 'backtest':     return <Backtest />
    case 'broker':       return <BrokerPanel />
    case 'alerts':       return <AlertsTab />
    case 'system':       return <SystemTab />
    case 'audit':        return <ModelBehavior />
    case 'control':      return <ControlPlane />
    case 'agents':       return <AgentConsole />
    case 'selftest':     return <AppSelfTest />
    case 'gates':        return <LiveTradingGate />
    default:             return <Overview />
  }
}

export default function App() {
  useData()

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column',
                  background: 'var(--surface)', overflow: 'hidden' }}>
      <TopBar />
      {/* BackendConnectivityBanner renders null when backend is reachable */}
      <BackendConnectivityBanner />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, overflow: 'hidden' }}>
          <Content />
        </main>
      </div>
    </div>
  )
}
