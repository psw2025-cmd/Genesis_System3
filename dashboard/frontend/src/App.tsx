import { useStore } from './store'
import { useData } from './hooks/useData'
import { TopBar } from './components/TopBar'
import { Sidebar } from './components/Sidebar'
import { Overview } from './components/Overview'
import { TradeTab } from './components/TradeTab'
import { Positions } from './components/Positions'
import { AlertsTab } from './components/AlertsTab'
import { SystemTab } from './components/SystemTab'

function Content() {
  const { activeTab } = useStore()
  switch (activeTab) {
    case 'overview':    return <Overview />
    case 'trade':       return <TradeTab />
    case 'positions':   return <Positions />
    case 'performance': return (
      <div className="p-6 text-text-muted text-sm flex flex-col gap-2">
        <h2 className="text-text-primary font-semibold">Performance</h2>
        <p>ML accuracy charts, ρ history, and gate detail — coming in next iteration.</p>
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
    <div className="h-screen flex flex-col bg-surface overflow-hidden dark">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          <Content />
        </main>
      </div>
    </div>
  )
}
