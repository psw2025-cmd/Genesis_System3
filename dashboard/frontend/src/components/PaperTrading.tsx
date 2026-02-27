import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import axios from 'axios'
import { API_BASE } from '../config'
import DataSourceWarning from './DataSourceWarning'
import EmptyState from './EmptyState'
import ErrorBanner from './ErrorBanner'

export default function PaperTrading() {
  const [state, setState] = useState<any>(null)
  const [pnl, setPnl] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Use SSOT endpoint for consistency
        const [stateRes, pnlRes] = await Promise.all([
          axios.get(`${API_BASE}/api/state`),
          axios.get(`${API_BASE}/api/pnl`)
        ])
        setState(stateRes.data)
        setPnl(pnlRes.data || null)
        setError(null)
      } catch (error: any) {
        console.error('Error fetching trading data:', error)
        setError(error.message || 'Failed to fetch trading data')
        setState(null)
        setPnl(null)
      }
    }
    // Fetch immediately on mount
    fetchData()
    // Optimized polling: 3000ms (3 seconds) - ensures data is always fresh
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [])
  
  // Extract positions from state (SSOT)
  const positions = state?.positions || []
  const positionsSource = state?.positions_source || 'INTERNAL_UNVERIFIED'
  const dataSource = state?.data_source || 'not_ready'
  const brokerConnected = state?.broker?.connected || false
  const mode = state?.mode || 'PAPER'
  const stateVersion = state?.state_version || 0

  // Show error if present
  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Paper Trading Console</h2>
        <ErrorBanner
          endpoint={`${API_BASE}/api/state`}
          message={error}
          onRetry={() => window.location.reload()}
        />
      </div>
    )
  }
  
  // Add loading state check
  if (!state) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Paper Trading Console</h2>
        <div className="p-6 text-center text-gray-400">Loading trading data...</div>
      </div>
    )
  }

  // Process PnL history with proper timestamp handling
  const pnlHistory = (pnl?.history || []).map((item: any) => {
    // Ensure timestamp is in ISO format
    let timestamp = item.timestamp || item.date || item.time || new Date().toISOString()
    
    // If timestamp is not a valid ISO string, try to parse it
    if (typeof timestamp === 'string') {
      // Try parsing various formats
      const parsed = new Date(timestamp)
      if (isNaN(parsed.getTime())) {
        // Invalid date - use current time
        timestamp = new Date().toISOString()
      } else {
        // Valid date - ensure ISO format
        timestamp = parsed.toISOString()
      }
    } else if (timestamp instanceof Date) {
      timestamp = timestamp.toISOString()
    } else {
      // Fallback to current time
      timestamp = new Date().toISOString()
    }
    
    return {
      ...item,
      timestamp: timestamp,
      total_pnl: item.total_pnl || item.total_unrealized_pnl || 0
    }
  }).filter((item: any) => {
    // Filter out items with invalid timestamps
    const date = new Date(item.timestamp)
    return !isNaN(date.getTime())
  })
  
  const summary = pnl?.summary || {}
  
  // Calculate total unrealized PnL from positions if summary doesn't have it
  const totalUnrealized = positions.reduce((sum, p) => sum + (p.unrealized_pnl || 0), 0)
  const totalRealized = summary?.total_realized_pnl || 0
  const totalPnL = totalUnrealized + totalRealized

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

  const isRealData = dataSource === 'REAL' || dataSource === 'real'
  const canTrade = isRealData && brokerConnected
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Paper Trading Console</h2>
          <div className="text-sm text-gray-400 mt-1">
            State Version: {stateVersion} | Positions Source: {positionsSource}
          </div>
        </div>
        {positions.length > 0 && (
          <button
            disabled={!canTrade}
            onClick={async () => {
              if (!canTrade) {
                alert('Trading is disabled. Real data and broker connection required.')
                return
              }
              if (confirm(`Close ALL ${positions.length} positions? This action cannot be undone.`)) {
                try {
                  // Close all positions
                  const closePromises = positions.map((pos: any) => 
                    axios.post(`${API_BASE}/api/positions/${pos.position_id}/close`).catch(err => {
                      console.error(`Error closing position ${pos.position_id}:`, err)
                      return null
                    })
                  )
                  await Promise.all(closePromises)
                  
                  // Refresh data
                  const [posRes, pnlRes] = await Promise.all([
                    axios.get(`${API_BASE}/api/positions`),
                    axios.get(`${API_BASE}/api/pnl`)
                  ])
                  setPositions(posRes.data.positions || [])
                  setPnl(pnlRes.data)
                  alert('All positions closed successfully')
                } catch (error) {
                  console.error('Error closing all positions:', error)
                  alert('Failed to close some positions. Check console for details.')
                }
              }
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white font-bold"
          >
            Close All (Emergency)
          </button>
        )}
      </div>
      
      {/* Data Source Warning */}
      <DataSourceWarning 
        dataSource={dataSource}
        brokerConnected={brokerConnected}
        mode={mode}
      />
      
      {/* Position Source Warning */}
      {positionsSource === 'INTERNAL_UNVERIFIED' && positions.length > 0 && (
        <div className="bg-orange-900/20 border border-orange-700 p-3 rounded-lg">
          <div className="text-sm text-orange-300">
            ⚠️ Positions shown are <strong>INTERNAL (UNVERIFIED)</strong>. Broker is disconnected. 
            These positions may not match broker reality.
          </div>
        </div>
      )}

      {/* Open Positions */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Open Positions ({positions.length})</h3>
        {positions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left p-2">Position ID</th>
                  <th className="text-left p-2">Symbol</th>
                  <th className="text-right p-2">Qty</th>
                  <th className="text-right p-2">Entry</th>
                  <th className="text-right p-2">Current</th>
                  <th className="text-right p-2">Unrealized PnL</th>
                  <th className="text-right p-2">SL/Target</th>
                  <th className="text-left p-2">Provenance</th>
                  <th className="text-right p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos: any, idx: number) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-2">{pos.position_id || 'N/A'}</td>
                    <td className="p-2">{pos.symbol || pos.underlying || 'N/A'}</td>
                    <td className="text-right p-2">{pos.qty || pos.quantity || 0}</td>
                    <td className="text-right p-2">₹{pos.entry_price?.toFixed(2) || 'N/A'}</td>
                    <td className="text-right p-2">₹{pos.current_price?.toFixed(2) || pos.entry_price?.toFixed(2) || 'N/A'}</td>
                    <td className={`text-right p-2 ${(pos.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ₹{pos.unrealized_pnl?.toFixed(2) || '0.00'}
                    </td>
                    <td className="text-right p-2 text-xs">
                      SL: ₹{pos.stop_loss?.toFixed(2) || 'N/A'}<br/>
                      TG: ₹{pos.target?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="text-left p-2 text-xs text-gray-400">
                      {pos.signal_source ? (
                        <>
                          Signal: {pos.signal_source}<br/>
                          {pos.entry_time && `Entry: ${new Date(pos.entry_time).toLocaleString()}`}
                          {pos.confidence && ` | Conf: ${(pos.confidence * 100).toFixed(0)}%`}
                        </>
                      ) : (
                        'N/A'
                      )}
                    </td>
                    <td className="text-right p-2">
                      <button
                        onClick={async () => {
                          if (confirm(`Close position ${pos.position_id}?`)) {
                            try {
                              await axios.post(`${API_BASE}/api/positions/${pos.position_id}/close`)
                              // Refresh data
                              const [posRes, pnlRes] = await Promise.all([
                                axios.get(`${API_BASE}/api/positions`),
                                axios.get(`${API_BASE}/api/pnl`)
                              ])
                              setPositions(posRes.data.positions || [])
                              setPnl(pnlRes.data)
                            } catch (error) {
                              console.error('Error closing position:', error)
                              alert('Failed to close position')
                            }
                          }
                        }}
                        className="px-2 py-1 bg-red-600 rounded hover:bg-red-700 text-xs"
                      >
                        Close
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-gray-400">No open positions</div>
        )}
      </div>

      {/* PnL Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equity Curve */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Equity Curve</h3>
          {pnlHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={pnlHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(v) => {
                    try {
                      const date = new Date(v)
                      return isNaN(date.getTime()) ? 'Invalid' : date.toLocaleTimeString()
                    } catch {
                      return 'Invalid'
                    }
                  }} 
                />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="total_pnl" stroke="#8884d8" name="Total PnL" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No PnL data available</div>
          )}
        </div>

        {/* PnL Summary */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">PnL Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Total PnL:</span>
              <span className={`font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ₹{totalPnL.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Unrealized:</span>
              <span className={`${totalUnrealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ₹{totalUnrealized.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Realized:</span>
              <span className={`${totalRealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ₹{totalRealized.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Open Positions:</span>
              <span>{positions.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Win Rate */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Win Rate</h3>
        {summary.total_trades > 0 ? (
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Winning', value: summary.winning_trades || 0 },
                      { name: 'Losing', value: summary.losing_trades || 0 }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[0, 1].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="text-center">
                <div className="text-3xl font-bold">{summary.win_rate?.toFixed(1) || 0}%</div>
                <div className="text-sm text-gray-400">Win Rate</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-400">No trades completed yet</div>
          )}
      </div>

      {/* Risk Panel */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Risk Panel</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-400">Max Positions</div>
            <div className="text-2xl font-bold">5</div>
            <div className="text-xs text-gray-500">Current: {positions.length}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Total Exposure</div>
            <div className="text-2xl font-bold">
              ₹{positions.reduce((sum, p) => sum + ((p.entry_price || 0) * (p.qty || 0)), 0).toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Kill Switch</div>
            <div className="text-2xl font-bold text-green-400">ACTIVE</div>
            <div className="text-xs text-gray-500">Trades disabled by default</div>
          </div>
        </div>
      </div>
    </div>
  )
}
