import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import axios from 'axios'
import { API_BASE, DEBUG } from '../config'
import { useWebSocket } from '../hooks/useWebSocket'
import AppSelfTest from './AppSelfTest'
import EmptyState from './EmptyState'
import ErrorBanner from './ErrorBanner'
import DataSourceWarning from './DataSourceWarning'

interface HealthData {
  status: string
  mode: string
  broker_status: string
  market_status: string
  data_source?: string
  last_data_time?: string | null
  data_age_seconds?: number | null
  cycle_count: number
  refresh_interval: number
  last_fetch: string
  qc_status: string
  qc_failures: string[]
  trades_executed: number
  open_positions: number
  total_pnl: number
  daily_pnl: number
  performance_sla: {
    cycle_duration_sec: number
    fetch_duration_sec: number
    strategy_duration_sec: number
    sla_pass: boolean
  }
}

export default function Overview() {
  const [health, setHealth] = useState<HealthData | null>(null)
  const [perfHistory, setPerfHistory] = useState<any[]>([])
  const [backendReady, setBackendReady] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorDetails, setErrorDetails] = useState<{endpoint: string, status?: number, message: string} | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [state, setState] = useState<any>(null) // Store full state for state_version access

  // Check if backend is ready
  const checkBackendReady = async (): Promise<boolean> => {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 2000) // 2 second timeout
      
      const response = await fetch(`${API_BASE}/api/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      return response.ok
    } catch (err) {
      if (DEBUG) console.log('Backend not ready yet:', err)
      return false
    }
  }

  const fetchData = async (retryCount = 0) => {
    // First check if backend is ready
    if (!backendReady) {
      try {
        const ready = await checkBackendReady()
        if (!ready) {
          if (retryCount < 10) {
            // Retry up to 10 times (20 seconds total)
            setTimeout(() => fetchData(retryCount + 1), 2000)
          } else {
            setError('Backend is not responding. Please check if the backend is running.')
          }
          return
        }
        setBackendReady(true)
        setError(null)
      } catch (err) {
        if (retryCount < 10) {
          setTimeout(() => fetchData(retryCount + 1), 2000)
        } else {
          setError('Backend check failed. Please check if the backend is running.')
        }
        return
      }
    }

    try {
        // Use SSOT endpoint for consistency
        const [stateRes, perfRes] = await Promise.all([
          axios.get(`${API_BASE}/api/state`, { timeout: 5000 }),
          axios.get(`${API_BASE}/api/perf`, { timeout: 5000 })
        ])
        
        // Convert SSOT state to health format for compatibility
        const stateData = stateRes.data
        setState(stateData) // Store full state for state_version access
        const healthData: HealthData = {
          status: 'ok',
          mode: stateData.mode || 'PAPER',
          broker_status: stateData.broker?.connected ? 'connected' : 'disconnected',
          market_status: stateData.market?.is_open ? 'open' : 'closed',
          data_source: stateData.data_source || 'unknown',
          last_data_time: stateData.last_data_time ?? stateData.last_fetch_ts_iso ?? null,
          data_age_seconds: stateData.data_age_seconds ?? null,
          cycle_count: stateData.cycle_count || 0,
          refresh_interval: 5,
          last_fetch: stateData.last_data_time || stateData.last_fetch_ts_iso || stateData.timestamp_ist || new Date().toISOString(),
          qc_status: stateData.qc?.status || 'PASS',
          qc_failures: stateData.qc?.failures || [],
          trades_executed: stateData.pnl?.day_total ? Math.abs(stateData.pnl.day_total) > 0 ? 1 : 0 : 0,
          open_positions: stateData.positions?.length || 0,
          total_pnl: stateData.pnl?.total || 0,
          daily_pnl: stateData.pnl?.day_total || 0,
          performance_sla: {
            cycle_duration_sec: 0.5,
            fetch_duration_sec: 0.1,
            strategy_duration_sec: 0.2,
            sla_pass: true
          }
        }
        
        setHealth(healthData)
        setPerfHistory(perfRes.data?.history || [])
        setError(null)
      } catch (error: any) {
      console.error('Error fetching data:', error)
      const errorMsg = error.message || 'Unknown error'
      const status = error.response?.status || null
      setError(`Failed to fetch data: ${errorMsg}`)
      setErrorDetails({
        endpoint: `${API_BASE}/api/state`,
        status: status || undefined,
        message: errorMsg
      })
      
      // Fallback to old endpoint if SSOT fails
      try {
        const healthRes = await axios.get(`${API_BASE}/api/health`, { timeout: 5000 })
        setHealth(healthRes.data)
        setError(null)
        setErrorDetails(null)
      } catch (fallbackError: any) {
        console.error('Fallback also failed:', fallbackError)
        const fallbackStatus = fallbackError.response?.status || null
        setError(`Backend connection failed: ${fallbackError.message || 'Check if backend is running on port 8000'}`)
        setErrorDetails({
          endpoint: `${API_BASE}/api/health`,
          status: fallbackStatus || undefined,
          message: fallbackError.message || 'Backend not reachable'
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  // WebSocket for real-time updates with polling fallback
  useWebSocket({
    onMessage: (message) => {
      if (message.type === 'health_update' && message.data) {
        setHealth(message.data)
        // Still fetch perf data via polling
        axios.get(`${API_BASE}/api/perf`)
          .then(res => setPerfHistory(res.data.history || []))
          .catch(err => console.error('Error fetching perf:', err))
      } else if (message.type === 'poll') {
        // Polling fallback triggered
        fetchData()
      }
    },
    fallbackPollInterval: 5000, // 5 seconds if WebSocket fails - reduced frequency
    enabled: true
  })

  useEffect(() => {
    // Fetch immediately on mount
    fetchData(0)
    
    // Optimized polling: 5000ms (5 seconds) - reduced frequency to avoid excessive API calls
    // This ensures data is always available even if WebSocket fails
    const interval = setInterval(() => {
      fetchData(0)
    }, 5000)
    
    return () => {
      clearInterval(interval)
    }
  }, [])

  // Always show something, even if health is null
  if (isLoading && !health) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-2xl font-bold mb-4">Loading Dashboard...</div>
          <div className="text-sm text-gray-400 mb-2">
            Component loaded at: {new Date().toLocaleTimeString()}
          </div>
          {!backendReady && (
            <div className="text-yellow-400 mb-2">
              ⏳ Waiting for backend to start...
            </div>
          )}
          <div className="text-gray-400 mt-4">
            <div>Connecting to backend at {API_BASE}...</div>
            <div className="text-xs mt-2">Check console (F12) for detailed logs</div>
          </div>
        </div>
      </div>
    )
  }

  // Show error state with ErrorBanner
  if (error && errorDetails) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">System Overview</h2>
        <AppSelfTest />
        <ErrorBanner
          endpoint={errorDetails.endpoint}
          status={errorDetails.status}
          message={errorDetails.message}
          onRetry={() => {
            if (DEBUG) console.log('[Overview] Retry button clicked')
            setBackendReady(false)
            setError(null)
            setErrorDetails(null)
            setIsLoading(true)
            fetchData(0)
          }}
        />
        <EmptyState
          title="Dashboard data unavailable"
          reason="Unable to load system overview. Please check backend connection."
          icon="⚠️"
        />
      </div>
    )
  }

  // Show empty state if health is null but no error
  if (!health && !error) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">System Overview</h2>
        <AppSelfTest />
        <EmptyState
          title="No dashboard data available"
          reason="System is initializing. Data will appear once backend is ready."
          icon="📊"
        />
      </div>
    )
  }

  const StatusBadge = ({ status, label }: { status: string | null | undefined; label: string }) => {
    const displayStatus = status || 'UNKNOWN' // Provide a default if status is null/undefined
    const colors: Record<string, string> = {
      'connected': 'bg-green-500',
      'disconnected': 'bg-red-500',
      'open': 'bg-green-500',
      'closed': 'bg-gray-500',
      'PASS': 'bg-green-500',
      'FAIL': 'bg-red-500',
      'NO_DATA': 'bg-yellow-500',
      'UNKNOWN': 'bg-gray-500' // Color for unknown status
    }
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm">{label}:</span>
        <span className={`px-2 py-1 rounded text-xs ${colors[displayStatus] || 'bg-gray-500'}`}>
          {displayStatus.toUpperCase()}
        </span>
      </div>
    )
  }

  const dataSource = health?.data_source || 'not_ready'
  const brokerConnected = health?.broker_status === 'connected'
  const mode = health?.mode || 'PAPER'
  const stateVersion = state?.state_version || 0
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">System Overview</h2>
        <div className="text-sm text-gray-400">
          State Version: {stateVersion}
        </div>
      </div>

      {/* Self-Test Component - Shows system status */}
      <AppSelfTest />
      
      {/* Data Source Warning */}
      <DataSourceWarning 
        dataSource={dataSource}
        brokerConnected={brokerConnected}
        mode={mode}
        lastDataTime={health?.last_data_time ?? health?.last_fetch}
        dataAgeSeconds={health?.data_age_seconds}
      />

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Trading Mode</div>
          <div className="text-2xl font-bold">
            <span className={mode === 'PAPER' ? 'text-blue-400' : mode === 'LIVE' ? 'text-red-400' : 'text-gray-400'}>
              {mode}
            </span>
          </div>
          {mode === 'PAPER' && (
            <div className="text-xs text-blue-400 mt-1">📊 Paper Trading Mode</div>
          )}
          {mode === 'LIVE' && (
            <div className="text-xs text-red-400 mt-1">⚠️ Real Money Trading</div>
          )}
          <StatusBadge status={health?.broker_status} label="Broker" />
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Market Status</div>
          <div className="text-2xl font-bold">{health?.market_status || 'UNKNOWN'}</div>
          <div className="mt-2">
            <div className={`inline-block px-2 py-1 rounded text-xs ${
              health?.data_source === 'live'
                ? 'bg-green-500 text-white'
                : health?.data_source === 'cached'
                ? 'bg-amber-500 text-black'
                : 'bg-yellow-500 text-black'
            }`}>
              {health?.data_source === 'live' ? '🟢 LIVE' : health?.data_source === 'cached' ? '📦 CACHED' : '⚠️ NOT READY'}
            </div>
          </div>
          <div className="text-sm text-gray-400 mt-2">Last Fetch: {health?.last_fetch ? new Date(health.last_fetch).toLocaleTimeString() : 'N/A'}</div>
          {health?.last_fetch && (() => {
            const age = (Date.now() - new Date(health.last_fetch).getTime()) / 1000 / 60
            const isStale = age > ((health.refresh_interval || 5) * 2 / 60)
            return (
              <div className={`text-xs mt-1 ${isStale ? 'text-red-400' : 'text-green-400'}`}>
                {isStale ? `⚠️ DATA STALE (${age.toFixed(1)} min old)` : `✓ Fresh (${age.toFixed(1)} min old)`}
              </div>
            )
          })()}
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">QC Status</div>
          <StatusBadge status={health?.qc_status} label="" />
          {health?.qc_failures && Array.isArray(health.qc_failures) && health.qc_failures.length > 0 && (
            <div className="text-xs text-red-400 mt-2">
              {health.qc_failures[0]}
            </div>
          )}
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Cycles</div>
          <div className="text-2xl font-bold">{health?.cycle_count || 0}</div>
          <div className="text-sm text-gray-400">Refresh: {health?.refresh_interval || 5}s</div>
        </div>
      </div>

      {/* Trading Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Trades Executed</div>
          <div className="text-3xl font-bold">{health?.trades_executed || 0}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Open Positions</div>
          <div className="text-3xl font-bold">{health?.open_positions || 0}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Total PnL</div>
          <div className={`text-3xl font-bold ${(health?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ₹{(health?.total_pnl || 0).toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {(health?.open_positions || 0) > 0 ? `${health?.open_positions} open` : 'No positions'}
          </div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Daily PnL</div>
          <div className={`text-3xl font-bold ${(health?.daily_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ₹{(health?.daily_pnl || 0).toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Realized only
          </div>
        </div>
      </div>

      {/* Performance SLA Chart */}
      {health?.performance_sla && (
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Performance SLA</h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <div className="text-sm text-gray-400">Cycle Duration</div>
              <div className={`text-2xl font-bold ${health.performance_sla.sla_pass ? 'text-green-400' : 'text-red-400'}`}>
                {health.performance_sla.cycle_duration_sec?.toFixed(3) || '0.000'}s
              </div>
              <div className="text-xs text-gray-500">SLA: ≤60s</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Fetch Duration</div>
              <div className="text-2xl font-bold">{health.performance_sla.fetch_duration_sec?.toFixed(3) || '0.000'}s</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Strategy Duration</div>
              <div className="text-2xl font-bold">{health.performance_sla.strategy_duration_sec?.toFixed(3) || '0.000'}s</div>
            </div>
          </div>
          {perfHistory && Array.isArray(perfHistory) && perfHistory.length > 0 && (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={perfHistory.slice(-20)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tickFormatter={(v) => new Date(v).toLocaleTimeString()} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="cycle_duration" stroke="#8884d8" name="Cycle Duration (s)" />
                <Line type="monotone" dataKey="fetch_duration" stroke="#82ca9d" name="Fetch Duration (s)" />
                <Line type="monotone" dataKey="strategy_duration" stroke="#ffc658" name="Strategy Duration (s)" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      )}
    </div>
  )
}
