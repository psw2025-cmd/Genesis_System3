import { useStore } from '../store'
import {
  LayoutDashboard, TrendingUp, BookOpen, BarChart3,
  Bell, Activity, Shield, ChevronRight
} from 'lucide-react'
import { cn } from '../lib/utils'

const TABS = [
  { id: 'overview',     label: 'Overview',    Icon: LayoutDashboard },
  { id: 'trade',        label: 'Trade',        Icon: TrendingUp },
  { id: 'positions',    label: 'Positions',    Icon: BookOpen },
  { id: 'performance',  label: 'Performance',  Icon: BarChart3 },
  { id: 'alerts',       label: 'Alerts',       Icon: Bell },
  { id: 'system',       label: 'System',       Icon: Activity },
  { id: 'gates',        label: 'Gate Matrix',  Icon: Shield },
]

export function Sidebar() {
  const { activeTab, setActiveTab, alerts } = useStore()
  const unread = alerts.filter(a => !a.read).length

  return (
    <aside className="w-52 flex-shrink-0 bg-surface-1 border-r border-border flex flex-col py-3">
      <nav className="flex-1 px-2 space-y-0.5">
        {TABS.map(({ id, label, Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn('nav-item w-full text-left', activeTab === id && 'active')}
          >
            <Icon size={15} className="flex-shrink-0" />
            <span className="flex-1">{label}</span>
            {id === 'alerts' && unread > 0 && (
              <span className="bg-down text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                {unread}
              </span>
            )}
            {activeTab === id && <ChevronRight size={12} className="text-text-muted" />}
          </button>
        ))}
      </nav>

      {/* Bottom: version */}
      <div className="px-4 pt-2 border-t border-border">
        <p className="text-[10px] text-text-muted font-mono">GENESIS SYSTEM3</p>
        <p className="text-[10px] text-text-muted">ANALYZER / PAPER MODE</p>
      </div>
    </aside>
  )
}
