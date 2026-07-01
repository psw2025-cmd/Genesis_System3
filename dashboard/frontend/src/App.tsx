import { useStore } from './store'
import { useData } from './hooks/useData'
import { TopBar } from './components/TopBar'
import { Sidebar } from './components/Sidebar'
import { Overview } from './components/Overview'
import { TradeTab } from './components/TradeTab'
import { Positions } from './components/Positions'
import { BrokerPanel } from './components/BrokerPanel'
import { PerformanceTab } from './components/PerformanceTab'
import { LiveTradingGate } from './components/LiveTradingGate'
import { AlertsTab } from './components/AlertsTab'
import { SystemTab } from './components/SystemTab'

function Content() {
  const { activeTab } = useStore()
  switch (activeTab) {
    case 'overview':    return <Overview />
    case 'trade':       return <TradeTab />
    case 'positions':   return <Positions />
    case 'broker':      return <BrokerPanel />
    case 'performance': return <PerformanceTab />
    case 'alerts':      return <AlertsTab />
    case 'system':      return <SystemTab />
    case 'gates':       return <LiveTradingGate />
    default:            return <TradeTab />
  }
}

export default function App() {
  useData()
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column',
                  background: 'var(--surface)', overflow: 'hidden' }}>
      <TopBar />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, overflow: 'hidden' }}>
          <Content />
        </main>
      </div>
    </div>
  )
}
