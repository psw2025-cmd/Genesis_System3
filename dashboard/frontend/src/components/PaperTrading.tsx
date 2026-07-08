import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import axios from 'axios'
import { API_BASE } from '../config'
import DataSourceWarning from './DataSourceWarning'
import ErrorBanner from './ErrorBanner'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

const formatMoney = (value: any) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return 'N/A'
  return `₹${n.toFixed(2)}`
}

const statusBadge = (label: string, tone: 'green' | 'yellow' | 'red' | 'gray' = 'gray') => {
  const classes: Record<string, string> = {
    green: 'bg-green-900/30 border-green-700 text-green-300',
    yellow: 'bg-yellow-900/30 border-yellow-700 text-yellow-300',
    red: 'bg-red-900/30 border-red-700 text-red-300',
    gray: 'bg-gray-900/40 border-gray-700 text-gray-300'
  }
  return <span className={`inline-flex items-center rounded border px-2 py-1 text-xs font-semibold ${classes[tone]}`}>{label}</span>
}

export default function PaperTrading() {
  const [state, setState] = useState<any>(null)
  const [pnl, setPnl] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const refreshData = async () => {
    const [stateRes, pnlRes] = await Promise.all([
      axios.get(`${API_BASE}/api/state`),
      axios.get(`${API_BASE}/api/pnl`)
    ])
    setState(stateRes.data)
    setPnl(pnlRes.data || null)
    setError(null)
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        await refreshData()
      } catch (error: any) {
        console.error('Error fetching trading data:', error)
        setError(error.message || 'Failed to fetch trading data')
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (error) {
    return (
      <div className="space-y-6 px-3 sm:px-0">
        <h2 className="text-2xl sm:text-3xl font-bold">Paper Trading Console</h2>
        <ErrorBanner
          endpoint={`${API_BASE}/api/state`}
          message={error}
          onRetry={() => window.location.reload()}
        />
      </div>
    )
  }

  if (!state) {
    return (
      <div className="space-y-6 px-3 sm:px-0">
        <h2 className="text-2xl sm:text-3xl font-bold">Paper Trading Console</h2>
        <div className="p-6 text-center text-gray-400">Loading trading data...</div>
      </div>
    )
  }

  const positions = state?.positions || []
  const positionsSource = state?.positions_source || 'INTERNAL_UNVERIFIED'
  const dataSource = state?.data_source || 'not_ready'
  const brokerConnected = Boolean(state?.broker?.connected)
  const brokerTradeUsable = Boolean(state?.broker?.trade_api_ready || state?.broker?.orders_ready || state?.broker?.trade_ready)
  const mode = state?.mode || 'PAPER'
  const stateVersion = state?.state_version || 0
  const isRealData = String(dataSource).toLowerCase() === 'real'
  const paperEngineReady = Boolean(state?.paper_engine_ready || state?.paper_engine?.ready || positions.length > 0)
  const canTrade = false
  const isInternalOnly = positionsSource !== 'BROKER_VERIFIED'

  const pnlHistory = (pnl?.history || []).map((item: any) => {
    let timestamp = item.timestamp || item.date || item.time || new Date().toISOString()
    if (typeof timestamp === 'string') {
      const parsed = new Date(timestamp)
      timestamp = isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString()
    } else if (timestamp instanceof Date) {
      timestamp = timestamp.toISOString()
    } else {
      timestamp = new Date().toISOString()
    }
    return {
      ...item,
      timestamp,
      total_pnl: item.total_pnl || item.total_unrealized_pnl || 0
    }
  }).filter((item: any) => !isNaN(new Date(item.timestamp).getTime()))

  const summary = pnl?.summary || {}
  const totalUnrealized = positions.reduce((sum: number, p: any) => sum + (Number(p.unrealized_pnl) || 0), 0)
  const totalRealized = Number(summary?.total_realized_pnl) || 0
  const totalPnL = totalUnrealized + totalRealized
  const exposure = positions.reduce((sum: number, p: any) => sum + ((Number(p.entry_price) || 0) * (Number(p.qty || p.quantity) || 0)), 0)

  const closePosition = async (positionId: string) => {
    alert('Close is disabled in truth-first paper view. Verify backend close route before enabling this action.')
  }

  return (
    <div className="space-y-6 px-3 sm:px-0 max-w-full overflow-x-hidden">
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-start">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold">Paper Trading Console</h2>
          <div className="text-xs sm:text-sm text-gray-400 mt-1 break-words">
            State Version: {stateVersion} | Positions Source: {positionsSource}
          </div>
        </div>
        {positions.length > 0 && (
          <button
            disabled
            title="Disabled until backend close route is verified for paper/internal positions."
            className="w-full sm:w-auto px-4 py-2 bg-gray-700 rounded text-gray-400 font-bold cursor-not-allowed"
          >
            Close All Disabled
          </button>
        )}
      </div>

      <div className="bg-gray-800 border border-gray-700 p-4 rounded-lg">
        <div className="font-bold text-gray-100 mb-3">PAPER MODE — NO REAL ORDERS</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
          <div>{statusBadge(`Broker Session: ${brokerConnected ? 'Connected' : 'Disconnected'}`, brokerConnected ? 'green' : 'red')}</div>
          <div>{statusBadge(`Trade API: ${brokerTradeUsable ? 'Ready' : 'Not Ready'}`, brokerTradeUsable ? 'green' : 'yellow')}</div>
          <div>{statusBadge(`Market Data: ${isRealData ? 'Ready' : 'Not Ready'}`, isRealData ? 'green' : 'yellow')}</div>
          <div>{statusBadge(`Positions: ${isInternalOnly ? 'Internal Only' : 'Broker Verified'}`, isInternalOnly ? 'yellow' : 'green')}</div>
          <div>{statusBadge('Trading: Disabled', 'red')}</div>
        </div>
        <div className="text-xs text-gray-400 mt-3">
          Broker login, trade API readiness, market data readiness, and paper position provenance are separate states. Internal paper rows are not broker truth.
        </div>
      </div>

      <DataSourceWarning dataSource={dataSource} brokerConnected={brokerConnected} mode={mode} />

      {isInternalOnly && positions.length > 0 && (
        <div className="bg-orange-900/20 border border-orange-700 p-3 rounded-lg">
          <div className="text-sm text-orange-300">
            ⚠️ Positions shown are <strong>INTERNAL / UNVERIFIED</strong>. They are simulated paper rows and may not match broker reality.
          </div>
        </div>
      )}

      <div className="bg-gray-800 p-4 sm:p-6 rounded-lg">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between mb-4">
          <h3 className="text-lg sm:text-xl font-bold">Open Positions ({positions.length})</h3>
          {isInternalOnly && statusBadge('INTERNAL_UNVERIFIED', 'yellow')}
        </div>

        {positions.length > 0 ? (
          <>
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-sm min-w-[880px]">
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
                  {positions.map((pos: any, idx: number) => {
                    const provenance = pos.signal_source || pos.source || pos.engine || pos.created_by
                    return (
                      <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                        <td className="p-2">{pos.position_id || 'N/A'}</td>
                        <td className="p-2">{pos.symbol || pos.underlying || 'N/A'}</td>
                        <td className="text-right p-2">{pos.qty || pos.quantity || 0}</td>
                        <td className="text-right p-2">{formatMoney(pos.entry_price)}</td>
                        <td className="text-right p-2">{formatMoney(pos.current_price ?? pos.entry_price)}</td>
                        <td className={`text-right p-2 ${(Number(pos.unrealized_pnl) || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {formatMoney(pos.unrealized_pnl || 0)}
                        </td>
                        <td className="text-right p-2 text-xs space-y-1">
                          <div>{pos.stop_loss ? `SL: ${formatMoney(pos.stop_loss)}` : statusBadge('SL N/A', 'yellow')}</div>
                          <div>{pos.target ? `TG: ${formatMoney(pos.target)}` : statusBadge('TG N/A', 'yellow')}</div>
                        </td>
                        <td className="text-left p-2 text-xs text-gray-300">
                          {provenance ? (
                            <>
                              <div>Source: {provenance}</div>
                              {pos.entry_time && <div>Entry: {new Date(pos.entry_time).toLocaleString()}</div>}
                              {pos.confidence && <div>Conf: {(pos.confidence * 100).toFixed(0)}%</div>}
                            </>
                          ) : (
                            statusBadge('INTERNAL_TEST_ONLY', 'yellow')
                          )}
                        </td>
                        <td className="text-right p-2">
                          <button
                            disabled
                            onClick={() => closePosition(pos.position_id)}
                            className="px-2 py-1 bg-gray-700 rounded text-gray-400 text-xs cursor-not-allowed"
                          >
                            Disabled
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="md:hidden space-y-3">
              {positions.map((pos: any, idx: number) => {
                const provenance = pos.signal_source || pos.source || pos.engine || pos.created_by
                return (
                  <div key={idx} className="bg-gray-900/60 border border-gray-700 rounded-lg p-4 space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="font-bold text-gray-100">{pos.symbol || pos.underlying || 'N/A'}</div>
                        <div className="text-xs text-gray-400">{pos.position_id || 'N/A'}</div>
                      </div>
                      {isInternalOnly ? statusBadge('PAPER_ONLY', 'yellow') : statusBadge('BROKER_VERIFIED', 'green')}
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><div className="text-gray-400 text-xs">Qty</div><div>{pos.qty || pos.quantity || 0}</div></div>
                      <div><div className="text-gray-400 text-xs">Entry</div><div>{formatMoney(pos.entry_price)}</div></div>
                      <div><div className="text-gray-400 text-xs">Current</div><div>{formatMoney(pos.current_price ?? pos.entry_price)}</div></div>
                      <div><div className="text-gray-400 text-xs">Unrealized PnL</div><div className={(Number(pos.unrealized_pnl) || 0) >= 0 ? 'text-green-400' : 'text-red-400'}>{formatMoney(pos.unrealized_pnl || 0)}</div></div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {pos.stop_loss ? statusBadge(`SL ${formatMoney(pos.stop_loss)}`, 'gray') : statusBadge('SL N/A', 'yellow')}
                      {pos.target ? statusBadge(`TG ${formatMoney(pos.target)}`, 'gray') : statusBadge('TG N/A', 'yellow')}
                      {provenance ? statusBadge(`Source: ${provenance}`, 'gray') : statusBadge('INTERNAL_TEST_ONLY', 'yellow')}
                    </div>
                    <button disabled className="w-full px-3 py-2 bg-gray-700 rounded text-gray-400 text-sm cursor-not-allowed">Close Disabled</button>
                  </div>
                )
              })}
            </div>
          </>
        ) : (
          <div className="bg-gray-900/50 border border-gray-700 p-6 rounded">
            <div className="font-bold text-gray-200">No open paper positions</div>
            <div className="text-sm text-gray-400 mt-2">Reason: paper engine has no open simulated position, market is closed, or broker/live data is not ready. This is not an error and no real order is placed.</div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-4 sm:p-6 rounded-lg min-w-0">
          <h3 className="text-lg sm:text-xl font-bold mb-4">Equity Curve</h3>
          {pnlHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={pnlHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tickFormatter={(v) => {
                  const date = new Date(v)
                  return isNaN(date.getTime()) ? 'Invalid' : date.toLocaleTimeString()
                }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="total_pnl" stroke="#8884d8" name="Total PnL" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="bg-gray-900/50 border border-gray-700 p-6 rounded"><div className="font-bold text-gray-200">No PnL curve yet</div><div className="text-sm text-gray-400 mt-2">Reason: no completed paper trade/PnL history rows are available. The chart will appear after paper engine records history.</div></div>
          )}
        </div>

        <div className="bg-gray-800 p-4 sm:p-6 rounded-lg">
          <h3 className="text-lg sm:text-xl font-bold mb-4">PnL Summary</h3>
          {isInternalOnly && <div className="mb-3">{statusBadge('Unverified internal paper PnL', 'yellow')}</div>}
          <div className="space-y-2 text-sm sm:text-base">
            <div className="flex justify-between gap-4"><span>Total PnL:</span><span className={`font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{formatMoney(totalPnL)}</span></div>
            <div className="flex justify-between gap-4"><span>Unrealized:</span><span className={`${totalUnrealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>{formatMoney(totalUnrealized)}</span></div>
            <div className="flex justify-between gap-4"><span>Realized:</span><span className={`${totalRealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>{formatMoney(totalRealized)}</span></div>
            <div className="flex justify-between gap-4"><span>Open Positions:</span><span>{positions.length}</span></div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-4 sm:p-6 rounded-lg">
        <h3 className="text-lg sm:text-xl font-bold mb-4">Win Rate</h3>
        {summary.total_trades > 0 ? (
          <div className="space-y-4">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={[{ name: 'Winning', value: summary.winning_trades || 0 }, { name: 'Losing', value: summary.losing_trades || 0 }]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {[0, 1].map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center"><div className="text-3xl font-bold">{summary.win_rate?.toFixed(1) || 0}%</div><div className="text-sm text-gray-400">Win Rate</div></div>
          </div>
        ) : (
          <div className="bg-gray-900/50 border border-gray-700 p-6 rounded"><div className="font-bold text-gray-200">No completed paper trades yet</div><div className="text-sm text-gray-400 mt-2">Win rate needs closed paper trades. Live trading remains OFF.</div></div>
        )}
      </div>

      <div className="bg-gray-800 p-4 sm:p-6 rounded-lg">
        <h3 className="text-lg sm:text-xl font-bold mb-4">Risk Panel</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-gray-900/40 border border-gray-700 rounded p-4"><div className="text-sm text-gray-400">Max Positions</div><div className="text-2xl font-bold">5</div><div className="text-xs text-gray-500">Current: {positions.length}</div></div>
          <div className="bg-gray-900/40 border border-gray-700 rounded p-4"><div className="text-sm text-gray-400">Total Exposure</div><div className="text-2xl font-bold break-words">{formatMoney(exposure)}</div><div className="text-xs text-gray-500">{isInternalOnly ? 'Internal paper exposure only' : 'Broker verified exposure'}</div></div>
          <div className="bg-gray-900/40 border border-gray-700 rounded p-4"><div className="text-sm text-gray-400">Kill Switch</div><div className="text-2xl font-bold text-red-400">ACTIVE</div><div className="text-xs text-gray-500">Trades disabled by default</div></div>
        </div>
      </div>
    </div>
  )
}
