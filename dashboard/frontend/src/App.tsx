import { useEffect, useRef } from 'react'
import { useStore } from './store'
import { useData } from './hooks/useData'

// ── Layout ────────────────────────────────────────────────────────────
import { TopBar }    from './components/TopBar'
import { Sidebar, DASHBOARD_TAB_IDS } from './components/Sidebar'
import ErrorBoundary from './components/ErrorBoundary'
import { SystemHealthDiagnostics } from './components/SystemHealthDiagnostics'

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

// ── V5 Workspaces ─────────────────────────────────────────────────────
import { DecisionIntelligence } from './components/workspaces/DecisionIntelligence'
import { OptionsIntelligence }  from './components/workspaces/OptionsIntelligence'
import { MultibaggerResearch }  from './components/workspaces/MultibaggerResearch'
import { RiskAndScenarios }     from './components/workspaces/RiskAndScenarios'
import { DataIntegrity }        from './components/workspaces/DataIntegrity'
import { PredictionAudit }      from './components/workspaces/PredictionAudit'

// ── Tier B: Axios-based tabs (need axios dep, call backend directly) ───
import Signals       from './components/Signals'
import PaperTrading  from './components/PaperTrading'
import MLPerformance from './components/MLPerformance'
import { GenesisTab } from './components/GenesisTab'

function Content() {
  const { activeTab } = useStore()
  switch (activeTab) {
    case 'decision-intel': return <DecisionIntelligence />
    case 'options-intel':  return <OptionsIntelligence />
    case 'multibagger':    return <MultibaggerResearch />
    case 'risk-scenarios': return <RiskAndScenarios />
    case 'data-integrity': return <DataIntegrity />
    case 'prediction-audit': return <PredictionAudit />
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
    default:             return <DecisionIntelligence />
  }
}

function DashboardTabUrlSync() {
  const { activeTab, setActiveTab } = useStore()
  const initialized = useRef(false)

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true
      const requested = new URLSearchParams(window.location.search).get('tab')
      if (requested && DASHBOARD_TAB_IDS.has(requested) && requested !== activeTab) {
        setActiveTab(requested)
        return
      }
    }

    if (!DASHBOARD_TAB_IDS.has(activeTab)) return
    const url = new URL(window.location.href)
    if (url.searchParams.get('tab') !== activeTab) {
      url.searchParams.set('tab', activeTab)
      window.history.replaceState(null, '', url)
    }
  }, [activeTab, setActiveTab])

  return null
}

export default function App() {
  // The deployed dashboard is intentionally public/read-only while System3 is
  // ANALYZER/PAPER and LIVE is locked off. The backend still rejects anonymous
  // mutation requests; public visibility does not grant execution authority.
  useData()
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column',
                  background: 'var(--surface)', overflow: 'hidden' }}>
      <a className="skip-link" href="#dashboard-main">Skip to content</a>
      <DashboardTabUrlSync />
      <TopBar />
      {/*
        Deploy proofs still need production-proof-bar in the DOM, but it must stay visually hidden
        on every normal page. Visible API/SHA/ML chips live only under Data Integrity → System health.
      */}
      <SystemHealthDiagnostics variant="sr-only" />
      <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        <SidebarBackdrop />
        <Sidebar />
        <main id="dashboard-main" tabIndex={-1} style={{ flex: 1, minWidth: 0, minHeight: 0, overflow: 'hidden' }}>
          <ErrorBoundary>
            <Content />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}

function SidebarBackdrop() {
  const { sidebarOpen, setSidebarOpen } = useStore()
  if (!sidebarOpen) return null
  return (
    <button
      type="button"
      className="sidebar-backdrop"
      aria-label="Close navigation"
      onClick={() => setSidebarOpen(false)}
    />
  )
}
