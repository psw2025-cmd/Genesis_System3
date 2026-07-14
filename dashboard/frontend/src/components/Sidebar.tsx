import {
  LayoutDashboard, TrendingUp, BookOpen, Database,
  FileText, BarChart3, Brain,
  Bell, Activity, Shield, Layers, Sparkles, CheckCircle, FlaskConical
} from 'lucide-react'
import { useStore } from '../store'

const TABS = [
  { id: 'truth',       label: 'Truth Control', Icon: Shield,            group: 'main' },
  { id: 'genesis',     label: 'Genesis Brain', Icon: Sparkles,         group: 'main' },
  { id: 'e2e-proof',   label: 'E2E Proof',     Icon: CheckCircle,      group: 'main' },
  { id: 'overview',    label: 'Overview',      Icon: LayoutDashboard,  group: 'main' },
  { id: 'sim-live',    label: 'Sim Live',      Icon: FlaskConical,     group: 'main' },
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
  main:     'Command',
  market:   'Market Data',
  trading:  'Trading',
  analysis: 'Analysis',
  system:   'System',
}

export function Sidebar() {
  const { activeTab, setActiveTab, marketOpen, brokerConnected } = useStore()

  const groups = ['main', 'market', 'trading', 'analysis', 'system']

  return (
    <nav
      aria-label="Dashboard navigation"
      data-dashboard-navigation="sidebar"
      style={{
        width: '190px',
        background: 'var(--surface-2)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        overflowX: 'hidden',
        flexShrink: 0,
        padding: '10px 8px',
        gap: '8px',
      }}
    >
      {groups.map(group => {
        const groupTabs = TABS.filter(t => t.group === group)
        return (
          <div key={group} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
            <div style={{
              color: 'var(--text-mut)',
              fontSize: '10px',
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              padding: '8px 10px 4px',
            }}>
              {GROUP_LABELS[group]}
            </div>
            {groupTabs.map(({ id, label, Icon }) => {
              const active = activeTab === id
              const marketDim = ['chain', 'signals', 'trade'].includes(id) && !marketOpen
              const isGenesis = id === 'genesis'
              const isProof = id === 'e2e-proof'
              const isTruth = id === 'truth'
              const isSim = id === 'sim-live'
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setActiveTab(id)}
                  title={label}
                  aria-label={label}
                  aria-current={active ? 'page' : undefined}
                  data-dashboard-tab={id}
                  data-dashboard-tab-label={label}
                  style={{
                    width: '100%',
                    minHeight: '38px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    border: active ? '1px solid var(--accent)' : '1px solid transparent',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    background: active ? 'var(--surface-3)' : isGenesis || isProof || isTruth || isSim ? 'rgba(245, 158, 11, 0.08)' : 'transparent',
                    opacity: marketDim ? 0.45 : 1,
                    transition: 'all 0.12s',
                    position: 'relative',
                    color: active ? 'var(--text-primary)' : 'var(--text-muted)',
                    padding: '8px 10px',
                    textAlign: 'left',
                  }}
                >
                  <Icon
                    size={16}
                    color={active || isGenesis || isProof || isTruth || isSim ? 'var(--accent)' : 'var(--text-mut)'}
                    style={{ flexShrink: 0 }}
                  />
                  <span style={{
                    fontSize: '12px',
                    fontWeight: active || isGenesis || isProof || isTruth || isSim ? 700 : 600,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {label}
                  </span>
                  {id === 'broker' && (
                    <span style={{
                      marginLeft: 'auto',
                      width: '7px', height: '7px', borderRadius: '50%',
                      background: brokerConnected ? 'var(--up)' : 'var(--down)',
                    }} />
                  )}
                  {id === 'truth' && <span style={{ marginLeft: 'auto', fontSize: '10px' }}>TRUTH</span>}
                  {id === 'e2e-proof' && <span style={{ marginLeft: 'auto', fontSize: '10px' }}>PROOF</span>}
                  {id === 'sim-live' && <span style={{ marginLeft: 'auto', fontSize: '10px' }}>SIM</span>}
                  {id === 'gates' && <span style={{ marginLeft: 'auto', fontSize: '10px' }}>LOCK</span>}
                </button>
              )
            })}
          </div>
        )
      })}
    </nav>
  )
}
