import { useState } from 'react'
import {
  LayoutDashboard, TrendingUp, BookOpen, Database,
  LineChart, FileText, BarChart3, Brain,
  Bell, Activity, Shield, Layers, BarChart2,
  ChevronLeft, ChevronRight, AlertTriangle, Cpu,
  Microscope, FlaskConical, Settings, Bot, ClipboardCheck
} from 'lucide-react'
import { useStore } from '../store'
import { cn } from '../lib/utils'

const TABS = [
  // ── Dashboard ────────────────────────────────────────────────────────────
  { id: 'overview',     label: 'Overview',        Icon: LayoutDashboard, group: 'main' },
  // ── Market Data ──────────────────────────────────────────────────────────
  { id: 'chain',        label: 'Option Chain',    Icon: Layers,          group: 'market' },
  { id: 'analytics',   label: 'Chain Analytics', Icon: Microscope,      group: 'market' },
  { id: 'signals',      label: 'Signals',         Icon: TrendingUp,      group: 'market' },
  { id: 'charts',       label: 'Adv. Charts',     Icon: BarChart2,       group: 'market' },
  // ── Trading ──────────────────────────────────────────────────────────────
  { id: 'trade',        label: 'Trade',           Icon: FileText,        group: 'trading' },
  { id: 'paper',        label: 'Paper Trades',    Icon: BookOpen,        group: 'trading' },
  { id: 'positions',    label: 'Positions',       Icon: Database,        group: 'trading' },
  // ── Analysis ─────────────────────────────────────────────────────────────
  { id: 'performance',  label: 'Performance',     Icon: BarChart3,       group: 'analysis' },
  { id: 'risk',         label: 'Risk',            Icon: AlertTriangle,   group: 'analysis' },
  { id: 'backtest',     label: 'Backtest',        Icon: FlaskConical,    group: 'analysis' },
  { id: 'ml',           label: 'ML Model',        Icon: Brain,           group: 'analysis' },
  // ── System ───────────────────────────────────────────────────────────────
  { id: 'broker',       label: 'Broker',          Icon: Cpu,             group: 'system' },
  { id: 'alerts',       label: 'Alerts',          Icon: Bell,            group: 'system' },
  { id: 'system',       label: 'System',          Icon: Activity,        group: 'system' },
  { id: 'audit',        label: 'Audit / Logs',    Icon: LineChart,       group: 'system' },
  { id: 'control',      label: 'Control Plane',   Icon: Settings,        group: 'system' },
  { id: 'agents',       label: 'Agents',          Icon: Bot,             group: 'system' },
  { id: 'selftest',     label: 'Self-Test',       Icon: ClipboardCheck,  group: 'system' },
  { id: 'gates',        label: 'Live Gate',       Icon: Shield,          group: 'system' },
]

const GROUP_LABELS: Record<string, string> = {
  main:     'Dashboard',
  market:   'Market Data',
  trading:  'Trading',
  analysis: 'Analysis',
  system:   'System',
}

const SIDEBAR_COLLAPSED = 52
const SIDEBAR_EXPANDED  = 176

export function Sidebar() {
  const { activeTab, setActiveTab, marketOpen, brokerConnected } = useStore()
  const [expanded, setExpanded] = useState(false)
  const width = expanded ? SIDEBAR_EXPANDED : SIDEBAR_COLLAPSED

  const groups = ['main', 'market', 'trading', 'analysis', 'system']

  return (
    <nav style={{
      width: `${width}px`,
      background: 'var(--surface-2)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      flexShrink: 0,
      transition: 'width 0.18s ease',
    }}>
      {/* Expand / Collapse toggle */}
      <button
        onClick={() => setExpanded(e => !e)}
        title={expanded ? 'Collapse sidebar' : 'Expand sidebar'}
        style={{
          width: '100%',
          height: '36px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: expanded ? 'flex-end' : 'center',
          paddingRight: expanded ? '10px' : 0,
          border: 'none',
          cursor: 'pointer',
          background: 'transparent',
          borderBottom: '1px solid var(--border)',
          color: 'var(--text-mut)',
          flexShrink: 0,
        }}
      >
        {expanded
          ? <ChevronLeft size={14} />
          : <ChevronRight size={14} />
        }
      </button>

      {/* Scrollable tab area */}
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {groups.map(group => {
          const groupTabs = TABS.filter(t => t.group === group)
          return (
            <div key={group}>
              {/* Group label — only when expanded */}
              {expanded && (
                <div style={{
                  padding: '8px 10px 2px',
                  fontSize: '.55rem',
                  fontWeight: 700,
                  letterSpacing: '.1em',
                  textTransform: 'uppercase',
                  color: 'var(--text-mut)',
                  whiteSpace: 'nowrap',
                }}>
                  {GROUP_LABELS[group]}
                </div>
              )}

              {groupTabs.map(({ id, label, Icon }) => {
                const active = activeTab === id
                const marketDim = ['chain', 'analytics', 'signals', 'trade'].includes(id) && !marketOpen
                return (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                    title={expanded ? undefined : label}
                    style={{
                      width: '100%',
                      height: '40px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: expanded ? 'flex-start' : 'center',
                      gap: expanded ? '8px' : 0,
                      paddingLeft: expanded ? '12px' : 0,
                      border: 'none',
                      cursor: 'pointer',
                      background: active ? 'var(--surface-3)' : 'transparent',
                      borderLeft: active ? '2px solid var(--accent)' : '2px solid transparent',
                      opacity: marketDim ? 0.45 : 1,
                      transition: 'background 0.1s, opacity 0.1s',
                      position: 'relative',
                    }}
                  >
                    <Icon
                      size={15}
                      color={active ? 'var(--accent)' : 'var(--text-mut)'}
                      style={{ flexShrink: 0 }}
                    />
                    {expanded && (
                      <span style={{
                        fontSize: '.72rem',
                        fontWeight: active ? 600 : 400,
                        color: active ? 'var(--text-pri)' : 'var(--text-sec)',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {label}
                      </span>
                    )}
                    {/* Broker status dot */}
                    {id === 'broker' && (
                      <span style={{
                        position: 'absolute',
                        top: '7px',
                        right: expanded ? '10px' : '7px',
                        width: '5px', height: '5px', borderRadius: '50%',
                        background: brokerConnected ? 'var(--up)' : 'var(--down)',
                      }} />
                    )}
                    {/* Live gate lock */}
                    {id === 'gates' && (
                      <span style={{
                        position: 'absolute',
                        top: '7px',
                        right: expanded ? '10px' : '7px',
                        fontSize: '7px',
                      }}>🔒</span>
                    )}
                  </button>
                )
              })}

              {/* Group divider */}
              <div style={{ height: '1px', background: 'var(--border)', margin: '2px 6px' }} />
            </div>
          )
        })}
      </div>
    </nav>
  )
}
