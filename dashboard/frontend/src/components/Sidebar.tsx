import {
  LayoutDashboard, TrendingUp, BookOpen, Database,
  FileText, BarChart3, Brain,
  Bell, Activity, Shield, Layers, Sparkles, CheckCircle, FlaskConical,
  Search, Zap
} from 'lucide-react'
import { useStore } from '../store'

export const DASHBOARD_TABS = [
  { id: 'decision-intel', label: 'Decision Intel', Icon: Zap, group: 'main' },
  { id: 'truth',          label: 'Truth Control',  Icon: Shield,          group: 'main' },
  { id: 'genesis',        label: 'Genesis Brain',  Icon: Sparkles,        group: 'main' },
  { id: 'e2e-proof',      label: 'E2E Proof',      Icon: CheckCircle,     group: 'main' },
  { id: 'overview',       label: 'Overview',       Icon: LayoutDashboard, group: 'main' },
  { id: 'sim-live',       label: 'Sim Live',       Icon: FlaskConical,    group: 'main' },
  { id: 'options-intel',  label: 'Options Intel',  Icon: Layers,          group: 'market' },
  { id: 'chain',          label: 'Option Chain',   Icon: Layers,          group: 'market' },
  { id: 'signals',        label: 'Signals',        Icon: TrendingUp,      group: 'market' },
  { id: 'trade',          label: 'Trade',          Icon: FileText,        group: 'trading' },
  { id: 'paper',          label: 'Paper Trades',   Icon: BookOpen,        group: 'trading' },
  { id: 'positions',      label: 'Positions',      Icon: Database,        group: 'trading' },
  { id: 'risk-scenarios', label: 'Risk & Scenarios', Icon: Shield,        group: 'analysis' },
  { id: 'multibagger',    label: 'Multibagger V4', Icon: Sparkles,        group: 'analysis' },
  { id: 'prediction-audit', label: 'Prediction Audit', Icon: Search,       group: 'analysis' },
  { id: 'performance',    label: 'Performance',    Icon: BarChart3,       group: 'analysis' },
  { id: 'ml',             label: 'ML Model',       Icon: Brain,           group: 'analysis' },
  { id: 'data-integrity', label: 'Data Integrity', Icon: Database,        group: 'system' },
  { id: 'broker',         label: 'Broker',         Icon: Database,        group: 'system' },
  { id: 'alerts',         label: 'Alerts',         Icon: Bell,            group: 'system' },
  { id: 'system',         label: 'System',         Icon: Activity,        group: 'system' },
  { id: 'gates',          label: 'Live Gate',      Icon: Shield,          group: 'system' },
] as const

export const DASHBOARD_TAB_IDS: ReadonlySet<string> = new Set(DASHBOARD_TABS.map(tab => tab.id))

const GROUP_LABELS: Record<string, string> = {
  main:     'Command',
  market:   'Market Data',
  trading:  'Trading',
  analysis: 'Analysis',
  system:   'System',
}

export function Sidebar() {
  const { activeTab, setActiveTab, marketOpen, brokerConnected, sidebarOpen } = useStore()

  const groups = ['main', 'market', 'trading', 'analysis', 'system']

  return (
    <nav
      id="dashboard-sidebar"
      aria-label="Dashboard navigation"
      data-dashboard-navigation="sidebar"
      className={`dashboard-sidebar${sidebarOpen ? ' is-open' : ''}`}
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
        const groupTabs = DASHBOARD_TABS.filter(t => t.group === group)
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
              const isGenesis = id === 'genesis'
              const isProof = id === 'e2e-proof'
              const isTruth = id === 'truth'
              const isSim = id === 'sim-live'
              const highlight = isGenesis || isProof || isTruth || isSim
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
                    minHeight: '36px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    border: active ? '1px solid var(--accent)' : '1px solid transparent',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    background: active ? 'var(--surface-3)' : highlight ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
                    transition: 'all 0.12s',
                    position: 'relative',
                    color: active ? 'var(--text-pri)' : 'var(--text-sec)',
                    padding: '7px 10px',
                    textAlign: 'left',
                  }}
                >
                  <Icon
                    size={15}
                    color={active || highlight ? 'var(--accent)' : 'var(--text-mut)'}
                    style={{ flexShrink: 0 }}
                  />
                  <span style={{
                    fontSize: '12px',
                    fontWeight: active || highlight ? 700 : 500,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    color: 'inherit',
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
                  {id === 'truth' && <span style={{ marginLeft: 'auto', fontSize: '9px', color: 'var(--text-mut)' }}>TRUTH</span>}
                  {id === 'e2e-proof' && <span style={{ marginLeft: 'auto', fontSize: '9px', color: 'var(--text-mut)' }}>PROOF</span>}
                  {id === 'sim-live' && <span style={{ marginLeft: 'auto', fontSize: '9px', color: 'var(--text-mut)' }}>SIM</span>}
                  {id === 'gates' && <span style={{ marginLeft: 'auto', fontSize: '9px', color: 'var(--text-mut)' }}>LOCK</span>}
                  {['chain', 'signals', 'trade'].includes(id) && !marketOpen && (
                    <span style={{ marginLeft: 'auto', fontSize: '9px', color: 'var(--amber)' }}>POLL</span>
                  )}
                </button>
              )
            })}
          </div>
        )
      })}
    </nav>
  )
}
