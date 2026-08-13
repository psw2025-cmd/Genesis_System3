import { useEffect, useRef } from 'react'
import { useStore } from './store'
import { useData } from './hooks/useData'
import { brokerIsConnected, paperModeActive, systemRuntimeOk } from './lib/healthTruth'

// ── Layout ────────────────────────────────────────────────────────────
import { TopBar }    from './components/TopBar'
import { Sidebar, DASHBOARD_TAB_IDS } from './components/Sidebar'
import ErrorBoundary from './components/ErrorBoundary'

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

function ProductionProofBar() {
  const { autoGates, brokerConnected, health, wsStatus, deployInfo } = useStore()

  const gatesObj = (autoGates?.gates && typeof autoGates.gates === 'object') ? autoGates.gates : {}
  const proofList = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const mlGate = gatesObj.ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS || proofList.find((g: any) => /spearman|ml accuracy/i.test(String(g?.label || g?.gate_id || '')))
  const paperGate = gatesObj.REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF || proofList.find((g: any) => /paper lifecycle|provenance/i.test(String(g?.label || g?.gate_id || '')))

  const mlOk = Boolean(mlGate?.pass ?? mlGate?.ok)
  const paperGateOk = Boolean(paperGate?.pass ?? paperGate?.ok)
  const paperOk = paperGateOk || paperModeActive(health)
  const dhanOk = brokerIsConnected(health, brokerConnected)
  const runtimeOk = systemRuntimeOk(health)
  const wsTone: 'ok' | 'warn' | 'error' = wsStatus === 'live' ? 'ok' : wsStatus === 'error' ? 'error' : 'warn'
  const mlLabel = mlOk
    ? `ρ=${mlGate?.latest_rho ?? 'ok'}`
    : `ML ${(mlGate?.days_recorded ?? 0)}/${(mlGate?.days_required ?? 5)}d`
  const wsLabel = wsStatus === 'live' ? 'WS LIVE' : `WS ${wsStatus.toUpperCase()}`

  const proofItems: Array<[string, string, 'ok' | 'warn' | 'error']> = [
    ['SYSTEM', runtimeOk ? String(health?.mode || health?.status || 'OK').toUpperCase() : 'PENDING', runtimeOk ? 'ok' : 'error'],
    ['API', runtimeOk ? 'RESPONDING' : 'CHECK', runtimeOk ? 'ok' : 'warn'],
    ['WS', wsLabel, wsTone],
    ['DATA', dhanOk ? 'DHAN' : 'DHAN REQ', dhanOk ? 'ok' : 'error'],
    ['ML', mlLabel, mlOk ? 'ok' : 'warn'],
    ['PAPER', paperOk ? (paperGateOk ? 'OK' : 'MODE ON') : 'PENDING', paperOk ? 'ok' : 'warn'],
    ['UI', 'RENDERED', 'ok'],
    ['SHA', deployInfo?.git_sha ? String(deployInfo.git_sha).slice(0, 7).toUpperCase() : '…', deployInfo?.git_sha ? 'ok' : 'warn'],
  ]

  const toneColor = {
    ok: { bg: 'rgba(34,197,94,.12)', border: 'rgba(34,197,94,.4)', dot: '#22c55e', text: '#4ade80' },
    warn: { bg: 'rgba(245,158,11,.12)', border: 'rgba(245,158,11,.4)', dot: '#f59e0b', text: '#fbbf24' },
    error: { bg: 'rgba(239,68,68,.12)', border: 'rgba(239,68,68,.4)', dot: '#ef4444', text: '#fca5a5' },
  }

  return (
    <div
      data-testid="production-proof-bar"
      role="status"
      aria-live="polite"
      aria-label="Production proof status"
      title="System3 runtime proof status"
      style={{
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 12px',
        minHeight: '40px',
        background: 'linear-gradient(90deg, rgba(15,23,42,.95) 0%, rgba(20,30,50,.95) 100%)',
        borderBottom: `2px solid ${runtimeOk ? 'rgba(34,197,94,.5)' : 'rgba(239,68,68,.5)'}`,
        overflowX: 'auto',
      }}
    >
      <span style={{
        color: 'rgba(100,200,255,0.9)',
        fontSize: '11px',
        fontFamily: 'monospace',
        fontWeight: 800,
        letterSpacing: '0.12em',
        whiteSpace: 'nowrap',
      }}>≣ GENESIS v2.0</span>
      
      {proofItems.map(([label, value, tone]) => {
        const colors = toneColor[tone]
        return (
        <div
          key={label}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            borderRadius: '4px',
            background: colors.bg,
            border: `1px solid ${colors.border}`,
            whiteSpace: 'nowrap',
            boxShadow: tone === 'ok' ? '0 0 8px rgba(34,197,94,.15)' : 'none',
          }}
        >
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: colors.dot,
            boxShadow: `0 0 4px ${colors.dot}`,
            animation: tone === 'error' ? 'pulse 2s infinite' : 'none',
          }} />
          
          <span style={{
            color: 'rgba(200,220,255,0.8)',
            fontSize: '9px',
            fontFamily: 'monospace',
            fontWeight: 700,
            letterSpacing: '0.05em',
          }}>{label}</span>
          <span style={{
            color: colors.text,
            fontSize: '10px',
            fontFamily: 'monospace',
            fontWeight: 800,
          }}>{value}</span>
        </div>
        )
      })}
    </div>
  )
}

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
      <ProductionProofBar />
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
