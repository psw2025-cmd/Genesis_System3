import { lazy, Suspense, useEffect, useLayoutEffect, useRef } from 'react'
import { useStore } from './store'
import { useData } from './hooks/useData'

// ── Layout ────────────────────────────────────────────────────────────
import { TopBar }    from './components/TopBar'
import { TruthStrip } from './components/TruthStrip'
import { Sidebar, DASHBOARD_TAB_IDS } from './components/Sidebar'
import { SystemTruthControl } from './components/SystemTruthControl'
import ErrorBoundary from './components/ErrorBoundary'
import { SystemHealthDiagnostics } from './components/SystemHealthDiagnostics'
import { AutonomousLoopBanner } from './components/AutonomousLoopBanner'
import { DeploymentTruthFooter } from './components/DeploymentTruthFooter'

// Route-level chunks keep the initial dashboard light and load each workspace on demand.
const Overview = lazy(() => import('./components/Overview').then((m) => ({ default: m.Overview })))
const TradeTab = lazy(() => import('./components/TradeTab').then((m) => ({ default: m.TradeTab })))
const Positions = lazy(() => import('./components/Positions').then((m) => ({ default: m.Positions })))
const BrokerProofPanel = lazy(() => import('./components/BrokerProofPanel').then((m) => ({ default: m.BrokerProofPanel })))
const OptionChain = lazy(() => import('./components/OptionChain').then((m) => ({ default: m.OptionChain })))
const AlertsTab = lazy(() => import('./components/AlertsTab').then((m) => ({ default: m.AlertsTab })))
const SystemTab = lazy(() => import('./components/SystemTab').then((m) => ({ default: m.SystemTab })))
const LiveTradingGate = lazy(() => import('./components/LiveTradingGate').then((m) => ({ default: m.LiveTradingGate })))
const PerformanceTab = lazy(() => import('./components/PerformanceTab').then((m) => ({ default: m.PerformanceTab })))
const EndToEndProof = lazy(() => import('./components/EndToEndProof').then((m) => ({ default: m.EndToEndProof })))
const LiveSimulation = lazy(() => import('./components/LiveSimulation').then((m) => ({ default: m.LiveSimulation })))
const MobileTradingHub = lazy(() => import('./components/MobileTradingHub').then((m) => ({ default: m.MobileTradingHub })))
const DecisionIntelligence = lazy(() => import('./components/workspaces/DecisionIntelligence').then((m) => ({ default: m.DecisionIntelligence })))
const OptionsIntelligence = lazy(() => import('./components/workspaces/OptionsIntelligence').then((m) => ({ default: m.OptionsIntelligence })))
const MultibaggerResearch = lazy(() => import('./components/workspaces/MultibaggerResearch').then((m) => ({ default: m.MultibaggerResearch })))
const RiskAndScenarios = lazy(() => import('./components/workspaces/RiskAndScenarios').then((m) => ({ default: m.RiskAndScenarios })))
const DataIntegrity = lazy(() => import('./components/workspaces/DataIntegrity').then((m) => ({ default: m.DataIntegrity })))
const PredictionAudit = lazy(() => import('./components/workspaces/PredictionAudit').then((m) => ({ default: m.PredictionAudit })))
const Signals = lazy(() => import('./components/Signals'))
const PaperTrading = lazy(() => import('./components/PaperTrading'))
const MLPerformance = lazy(() => import('./components/MLPerformance'))
const SystemReadiness = lazy(() => import('./components/SystemReadiness'))
const GenesisTab = lazy(() => import('./components/GenesisTab').then((m) => ({ default: m.GenesisTab })))

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
    case 'system-readiness': return <SystemReadiness />
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
  useEffect(() => {
    // Keep navigation responsive after the first screen: warm the route chunks
    // once the dashboard has mounted so a later tab click cannot sit on the
    // Suspense fallback while the browser fetches its first module chunk.
    const timer = window.setTimeout(() => {
      void Promise.allSettled([
        import('./components/Overview'), import('./components/TradeTab'),
        import('./components/Positions'), import('./components/BrokerProofPanel'),
        import('./components/OptionChain'), import('./components/AlertsTab'),
        import('./components/SystemTab'), import('./components/LiveTradingGate'),
        import('./components/PerformanceTab'), import('./components/EndToEndProof'),
        import('./components/LiveSimulation'),
        import('./components/MobileTradingHub'),
        import('./components/workspaces/DecisionIntelligence'),
        import('./components/workspaces/OptionsIntelligence'),
        import('./components/workspaces/MultibaggerResearch'),
        import('./components/workspaces/RiskAndScenarios'),
        import('./components/workspaces/DataIntegrity'),
        import('./components/workspaces/PredictionAudit'),
        import('./components/Signals'), import('./components/PaperTrading'),
        import('./components/MLPerformance'), import('./components/SystemReadiness'),
        import('./components/GenesisTab'),
      ])
    }, 1000)
    return () => window.clearTimeout(timer)
  }, [])
  const activeTab = useStore((s) => s.activeTab)
  useLayoutEffect(() => {
    const main = document.getElementById('dashboard-main')
    if (!main) return
    for (const element of main.querySelectorAll<HTMLElement>('*')) {
      if (element.scrollTop > 0 || element.scrollLeft > 0) {
        element.scrollTop = 0
        element.scrollLeft = 0
      }
    }
  }, [activeTab])
  const mobileTradingRoute = new URLSearchParams(window.location.search).get('view') === 'mobile-trader'
  if (mobileTradingRoute) return <MobileTradingHub />

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column',
                  background: 'var(--surface)', overflow: 'hidden' }}>
      <a className="skip-link" href="#dashboard-main">Skip to content</a>
      <DashboardTabUrlSync />
      <TopBar />
      <TruthStrip />
      <AutonomousLoopBanner />
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
            <Suspense fallback={<div role="status" style={{ padding: 20 }}>Loading dashboard section…</div>}>
              <Content />
            </Suspense>
          </ErrorBoundary>
        </main>
      </div>
      <DeploymentTruthFooter />
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
