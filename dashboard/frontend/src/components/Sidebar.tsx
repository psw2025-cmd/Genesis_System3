import {
  LayoutDashboard, TrendingUp, BookOpen, Database,
  LineChart, FileText, BarChart3, Brain,
  Bell, Activity, Shield, Layers
} from 'lucide-react'
import { useStore } from '../store'
import { cn } from '../lib/utils'

const TABS = [
  { id: 'overview',    label: 'Overview',      Icon: LayoutDashboard,  group: 'main' },
  { id: 'chain',       label: 'Option Chain',  Icon: Layers,           group: 'market' },
  { id: 'signals',     label: 'Signals',       Icon: TrendingUp,       group: 'market' },
  { id: 'trade',       label: 'Trade',         Icon: FileText,         group: 'trading' },
  { id: 'paper',       label: 'Paper Trades',  Icon: BookOpen,         group: 'trading' },
  { id: 'positions',   label: 'Positions',     Icon: Database,         group: 'trading' },
  { id: 'performance', label: 'Performance',   Icon: BarChart3,        group: 'analysis' },
  { id: 'ml',          label: 'ML Model',      Icon: Brain,            group: 'analysis' },
  { id: 'broker',      label: 'Broker',        Icon: Database,         group: 'system' },
  { id: 'alerts',      label: 'Alerts',        Icon: Bell,             group: 'system' },
  { id: 'system',      label: 'System',        Icon: Activity,         group: 'system' },
  { id: 'gates',       label: 'Live Gate',     Icon: Shield,           group: 'system' },
]

const GROUP_LABELS: Record<string, string> = {
  main:     'Dashboard',
  market:   'Market Data',
  trading:  'Trading',
  analysis: 'Analysis',
  system:   'System',
}

export function Sidebar() {
  const { activeTab, setActiveTab, marketOpen, brokerConnected } = useStore()

  const groups = ['main', 'market', 'trading', 'analysis', 'system']

  return (
    <nav style={{
      width: '52px',
      background: 'var(--surface-2)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      flexShrink: 0,
    }}>
      {groups.map(group => {
        const groupTabs = TABS.filter(t => t.group === group)
        return (
          <div key={group}>
            {groupTabs.map(({ id, label, Icon }) => {
              const active = activeTab === id
              // Market-dependent tabs dim when market closed
              const marketDim = ['chain', 'signals', 'trade'].includes(id) && !marketOpen
              return (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  title={label}
                  style={{
                    width: '52px',
                    height: '44px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: 'none',
                    cursor: 'pointer',
                    background: active ? 'var(--surface-3)' : 'transparent',
                    borderLeft: active ? '2px solid var(--accent)' : '2px solid transparent',
                    opacity: marketDim ? 0.45 : 1,
                    transition: 'all 0.12s',
                    position: 'relative',
                  }}
                >
                  <Icon
                    size={16}
                    color={active ? 'var(--accent)' : 'var(--text-mut)'}
                  />
                  {/* Broker status dot */}
                  {id === 'broker' && (
                    <span style={{
                      position: 'absolute', top: '6px', right: '6px',
                      width: '6px', height: '6px', borderRadius: '50%',
                      background: brokerConnected ? 'var(--up)' : 'var(--down)',
                    }} />
                  )}
                  {/* Live gate lock icon */}
                  {id === 'gates' && (
                    <span style={{
                      position: 'absolute', top: '6px', right: '6px',
                      fontSize: '8px',
                    }}>🔒</span>
                  )}
                </button>
              )
            })}
            <div style={{ height: '1px', background: 'var(--border)', margin: '2px 6px' }} />
          </div>
        )
      })}
    </nav>
  )
}
