import { useStore } from '../store'
import { LayoutDashboard, TrendingUp, BookOpen, BarChart3,
         Bell, Activity, Shield, Database, ChevronRight } from 'lucide-react'
import { cn } from '../lib/utils'

const TABS = [
  { id: 'overview',    label: 'Overview',    Icon: LayoutDashboard },
  { id: 'trade',       label: 'Trade',        Icon: TrendingUp },
  { id: 'positions',   label: 'Positions',    Icon: BookOpen },
  { id: 'broker',      label: 'Broker Data',  Icon: Database },
  { id: 'performance', label: 'Performance',  Icon: BarChart3 },
  { id: 'alerts',      label: 'Alerts',       Icon: Bell },
  { id: 'system',      label: 'System',       Icon: Activity },
  { id: 'gates',       label: 'Gate Matrix',  Icon: Shield },
]

export function Sidebar() {
  const { activeTab, setActiveTab, alerts, brokerConnected } = useStore()
  const unread = alerts.filter((a: any) => !a.read).length

  return (
    <aside style={{
      width: '180px', flexShrink: 0,
      background: 'var(--surface-1)', borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', padding: '8px 0',
    }}>
      <nav style={{ flex: 1, padding: '0 8px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {TABS.map(({ id, label, Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn('nav-item', activeTab === id && 'active')}
          >
            <Icon size={14} style={{ flexShrink: 0 }} />
            <span style={{ flex: 1, fontSize: '.78rem' }}>{label}</span>
            {id === 'broker' && (
              <span style={{
                width: '6px', height: '6px', borderRadius: '50%', flexShrink: 0,
                background: brokerConnected ? 'var(--up)' : 'var(--down)'
              }} />
            )}
            {id === 'alerts' && unread > 0 && (
              <span style={{
                background: 'var(--down)', color: '#fff', fontSize: '.6rem',
                fontWeight: 700, padding: '1px 5px', borderRadius: '9999px'
              }}>{unread}</span>
            )}
            {activeTab === id && <ChevronRight size={11} style={{ color: 'var(--text-mut)' }} />}
          </button>
        ))}
      </nav>
      <div style={{ padding: '10px 16px', borderTop: '1px solid var(--border)' }}>
        <p style={{ fontSize: '.6rem', color: 'var(--text-mut)', fontFamily: 'var(--font-mono)' }}>GENESIS SYSTEM3</p>
        <p style={{ fontSize: '.6rem', color: 'var(--text-mut)' }}>ANALYZER / PAPER</p>
      </div>
    </aside>
  )
}
