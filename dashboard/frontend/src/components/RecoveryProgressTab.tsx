import { useState, useEffect, useRef } from 'react'
import {
  CheckCircle, AlertTriangle, Clock, RefreshCw,
  Search, Shield, Layers, Filter, Eye, Database
} from 'lucide-react'

interface RecoveryItem {
  id: string
  tab: string
  priority: string
  issue: string
  root_cause: string
  status: string
  last_verification: string
  evidence_timestamp: string
  deployed_revision: string
}

interface RecoverySummary {
  total_issues: number
  pass_count: number
  partial_count: number
  open_count: number
  blocked_count: number
  p0_count: number
  p1_count: number
  p2_count: number
}

interface RecoveryProgressData {
  summary: RecoverySummary
  deployed_revision: string
  last_verification_utc: string
  market_status: string
  market_label: string
  safety_locks: {
    live_trading_enabled: number
    paper_mode: string
    order_placement_allowed: boolean
    live_allowed: boolean
    market_status: string
  }
  items: RecoveryItem[]
}

const POLLING_INTERVAL_MS = 15000 // 15s automatic refresh without page reload

export function RecoveryProgressTab() {
  const [data, setData] = useState<RecoveryProgressData | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [lastFetched, setLastFetched] = useState<Date | null>(null)
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL')
  const [statusFilter, setStatusFilter] = useState<string>('ALL')
  const [tabFilter, setTabFilter] = useState<string>('ALL')
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false)

  const isMountedRef = useRef(true)

  const fetchData = async (isManual = false) => {
    if (isManual) setIsRefreshing(true)
    try {
      const res = await fetch('/api/recovery/progress')
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      }
      const json: RecoveryProgressData = await res.json()
      if (isMountedRef.current) {
        setData(json)
        setError(null)
        setLastFetched(new Date())
      }
    } catch (err: any) {
      if (isMountedRef.current) {
        setError(err.message || 'Failed to fetch recovery progress')
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false)
        if (isManual) setIsRefreshing(false)
      }
    }
  }

  useEffect(() => {
    isMountedRef.current = true
    fetchData()

    // Automatic polling interval without requiring page reloads
    const timer = setInterval(() => {
      fetchData()
    }, POLLING_INTERVAL_MS)

    return () => {
      isMountedRef.current = false
      clearInterval(timer)
    }
  }, [])

  if (loading && !data) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-sec)' }}>
        <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px' }} />
        <div>Loading Genesis System3 Recovery Progress...</div>
      </div>
    )
  }

  const items = data?.items || []
  const summary = data?.summary || {
    total_issues: 0,
    pass_count: 0,
    partial_count: 0,
    open_count: 0,
    blocked_count: 0,
    p0_count: 0,
    p1_count: 0,
    p2_count: 0,
  }

  const uniqueTabs = Array.from(new Set(items.map((i) => i.tab))).filter(Boolean)

  const filteredItems = items.filter((item) => {
    const matchesSearch =
      searchTerm === '' ||
      item.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.issue.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.root_cause.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.tab.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesPriority =
      priorityFilter === 'ALL' || item.priority.toUpperCase() === priorityFilter.toUpperCase()

    const matchesStatus =
      statusFilter === 'ALL' || item.status.toUpperCase() === statusFilter.toUpperCase()

    const matchesTab = tabFilter === 'ALL' || item.tab === tabFilter

    return matchesSearch && matchesPriority && matchesStatus && matchesTab
  })

  const marketIsClosed = data?.market_status === 'closed'

  return (
    <div style={{ padding: '20px', height: '100%', overflowY: 'auto' }}>
      {/* Header Banner */}
      <div
        style={{
          background: 'var(--surface-2)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '16px 20px',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: 'var(--text-pri)' }}>
                Genesis System3 — Recovery Progress Register
              </h2>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  padding: '3px 8px',
                  borderRadius: '4px',
                  background: 'rgba(59, 130, 246, 0.15)',
                  color: 'var(--accent)',
                  border: '1px solid var(--accent)',
                }}
              >
                23 TABS / 113 MICRO-CHECKS
              </span>
            </div>
            <p style={{ margin: '6px 0 0', fontSize: '12px', color: 'var(--text-sec)' }}>
              Read-only authoritative progress synced with Excel issue register and durable verification evidence.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {/* Market Status Chip */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 600,
                background: marketIsClosed ? 'rgba(234, 179, 8, 0.12)' : 'rgba(34, 197, 94, 0.12)',
                color: marketIsClosed ? 'var(--amber)' : 'var(--up)',
                border: `1px solid ${marketIsClosed ? 'var(--amber)' : 'var(--up)'}`,
              }}
            >
              <Clock size={14} />
              <span>{data?.market_label || (marketIsClosed ? 'LAST VERIFIED MARKET CLOSE' : 'MARKET OPEN')}</span>
            </div>

            {/* Permanent Safety Lock Chip */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 600,
                background: 'rgba(16, 185, 129, 0.1)',
                color: 'var(--up)',
                border: '1px solid var(--up)',
              }}
            >
              <Shield size={14} />
              <span>PAPER ONLY (LIVE DISABLED)</span>
            </div>

            {/* Refresh Button */}
            <button
              type="button"
              onClick={() => fetchData(true)}
              disabled={isRefreshing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                borderRadius: '6px',
                background: 'var(--surface-3)',
                border: '1px solid var(--border)',
                color: 'var(--text-pri)',
                fontSize: '12px',
                cursor: 'pointer',
              }}
            >
              <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
              <span>Auto-refreshing (15s)</span>
            </button>
          </div>
        </div>

        {/* Data Source Quality Banner */}
        <div
          style={{
            marginTop: '14px',
            padding: '10px 14px',
            borderRadius: '6px',
            background: 'var(--surface-3)',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            fontSize: '11px',
            color: 'var(--text-sec)',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-pri)' }}>Data Distinctions:</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--up)' }} />
            <span>LIVE (Exchange Active)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--amber)' }} />
            <span>LAST VERIFIED MARKET CLOSE (Exchange Closed)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#64748b' }} />
            <span>STALE / HISTORICAL</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--down)' }} />
            <span>UNAVAILABLE</span>
          </div>
          <div style={{ marginLeft: 'auto', color: 'var(--text-mut)' }}>
            Deployed Revision: <code style={{ color: 'var(--accent)' }}>{data?.deployed_revision?.slice(0, 10)}</code> | Last Verified: {lastFetched ? lastFetched.toLocaleTimeString() : 'N/A'}
          </div>
        </div>

        {/* Metric Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: '12px',
            marginTop: '16px',
          }}
        >
          <div style={{ background: 'var(--surface-3)', padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)' }}>Total Checks</div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-pri)', marginTop: '2px' }}>{summary.total_issues}</div>
          </div>
          <div style={{ background: 'var(--surface-3)', padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)' }}>Verified PASS</div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--up)', marginTop: '2px' }}>{summary.pass_count}</div>
          </div>
          <div style={{ background: 'var(--surface-3)', padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)' }}>Audited / Partial</div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--amber)', marginTop: '2px' }}>{summary.partial_count}</div>
          </div>
          <div style={{ background: 'var(--surface-3)', padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)' }}>Priority P0</div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: summary.p0_count > 0 ? 'var(--down)' : 'var(--up)', marginTop: '2px' }}>
              {summary.p0_count}
            </div>
          </div>
          <div style={{ background: 'var(--surface-3)', padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)' }}>Priority P1</div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--amber)', marginTop: '2px' }}>{summary.p1_count}</div>
          </div>
          <div style={{ background: 'var(--surface-3)', padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)' }}>Priority P2</div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent)', marginTop: '2px' }}>{summary.p2_count}</div>
          </div>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div
        style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
          flexWrap: 'wrap',
          marginBottom: '16px',
        }}
      >
        <div style={{ position: 'relative', flex: '1', minWidth: '240px' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-mut)' }} />
          <input
            type="text"
            placeholder="Search by Issue ID, Tab, or Keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 10px 8px 32px',
              borderRadius: '6px',
              border: '1px solid var(--border)',
              background: 'var(--surface-2)',
              color: 'var(--text-pri)',
              fontSize: '12px',
            }}
          />
        </div>

        {/* Priority Filter */}
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border)',
            background: 'var(--surface-2)',
            color: 'var(--text-pri)',
            fontSize: '12px',
          }}
        >
          <option value="ALL">All Priorities</option>
          <option value="P0">P0 (Critical)</option>
          <option value="P1">P1 (High)</option>
          <option value="P2">P2 (Medium)</option>
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border)',
            background: 'var(--surface-2)',
            color: 'var(--text-pri)',
            fontSize: '12px',
          }}
        >
          <option value="ALL">All Statuses</option>
          <option value="PASS">PASS</option>
          <option value="PARTIAL">PARTIAL</option>
          <option value="OPEN">OPEN</option>
          <option value="BLOCKED">BLOCKED</option>
        </select>

        {/* Tab Filter */}
        <select
          value={tabFilter}
          onChange={(e) => setTabFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border)',
            background: 'var(--surface-2)',
            color: 'var(--text-pri)',
            fontSize: '12px',
            maxWidth: '180px',
          }}
        >
          <option value="ALL">All 23 Tabs</option>
          {uniqueTabs.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        <div style={{ fontSize: '12px', color: 'var(--text-sec)', marginLeft: 'auto' }}>
          Showing <b>{filteredItems.length}</b> of <b>{items.length}</b> checks
        </div>
      </div>

      {/* Issues Table */}
      <div
        style={{
          background: 'var(--surface-2)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      >
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'var(--surface-3)', borderBottom: '1px solid var(--border)', color: 'var(--text-sec)' }}>
              <th style={{ padding: '10px 14px', width: '90px' }}>ID</th>
              <th style={{ padding: '10px 14px', width: '120px' }}>Tab</th>
              <th style={{ padding: '10px 14px', width: '70px' }}>Prio</th>
              <th style={{ padding: '10px 14px' }}>Issue / Micro-check</th>
              <th style={{ padding: '10px 14px' }}>Root Cause</th>
              <th style={{ padding: '10px 14px', width: '90px' }}>Status</th>
              <th style={{ padding: '10px 14px' }}>Latest Verification Evidence</th>
            </tr>
          </thead>
          <tbody>
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-mut)' }}>
                  No issues matching the selected filters.
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => {
                const isP0 = item.priority === 'P0'
                const isPass = item.status === 'PASS'
                return (
                  <tr
                    key={item.id}
                    style={{
                      borderBottom: '1px solid var(--border)',
                      background: isP0 ? 'rgba(239, 68, 68, 0.02)' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '10px 14px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--accent)' }}>
                      {item.id}
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-sec)', fontWeight: 500 }}>
                      {item.tab}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <span
                        style={{
                          fontSize: '10px',
                          fontWeight: 700,
                          padding: '2px 6px',
                          borderRadius: '4px',
                          background:
                            item.priority === 'P0'
                              ? 'rgba(239, 68, 68, 0.15)'
                              : item.priority === 'P1'
                              ? 'rgba(234, 179, 8, 0.15)'
                              : 'rgba(59, 130, 246, 0.15)',
                          color:
                            item.priority === 'P0'
                              ? 'var(--down)'
                              : item.priority === 'P1'
                              ? 'var(--amber)'
                              : 'var(--accent)',
                        }}
                      >
                        {item.priority}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-pri)', fontWeight: 500 }}>
                      {item.issue}
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-sec)', fontSize: '11px' }}>
                      {item.root_cause}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <span
                        style={{
                          fontSize: '10px',
                          fontWeight: 700,
                          padding: '2px 6px',
                          borderRadius: '4px',
                          background: isPass
                            ? 'rgba(34, 197, 94, 0.15)'
                            : item.status === 'PARTIAL'
                            ? 'rgba(234, 179, 8, 0.15)'
                            : 'rgba(148, 163, 184, 0.15)',
                          color: isPass
                            ? 'var(--up)'
                            : item.status === 'PARTIAL'
                            ? 'var(--amber)'
                            : 'var(--text-mut)',
                        }}
                      >
                        {item.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-sec)', fontSize: '11px' }}>
                      <div>{item.last_verification}</div>
                      <div style={{ color: 'var(--text-mut)', fontSize: '10px', marginTop: '2px' }}>
                        Rev: {item.deployed_revision.slice(0, 8)} | UTC: {item.evidence_timestamp.replace('T', ' ').slice(0, 19)}
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
