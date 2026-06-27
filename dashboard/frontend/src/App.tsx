import { useStore } from './store'
import { useData } from './hooks/useData'
import { TopBar } from './components/TopBar'
import { Sidebar } from './components/Sidebar'
import { Overview } from './components/Overview'
import { TradeTab } from './components/TradeTab'
import { Positions } from './components/Positions'
import { BrokerPanel } from './components/BrokerPanel'
import { AlertsTab } from './components/AlertsTab'
import { SystemTab } from './components/SystemTab'

function Content() {
  const { activeTab } = useStore()
  switch (activeTab) {
    case 'overview':    return <Overview />
    case 'trade':       return <TradeTab />
    case 'positions':   return <Positions />
    case 'broker':      return <BrokerPanel />
    case 'performance': return (
      <div style={{ padding: '24px', color: 'var(--text-mut)', fontSize: '.85rem' }}>
        <h2 style={{ color: 'var(--text-pri)', fontWeight: 600, marginBottom: '8px' }}>Performance</h2>
        <p>ML accuracy charts, ρ history, equity curve — coming next iteration.</p>
      </div>
    )
    case 'alerts':      return <AlertsTab />
    case 'system':      return <SystemTab />
    case 'gates':       return <Overview />
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
