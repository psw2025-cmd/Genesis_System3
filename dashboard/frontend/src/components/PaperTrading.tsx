import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import axios from 'axios'
import { API_BASE } from '../config'
import DataSourceWarning from './DataSourceWarning'
import ErrorBanner from './ErrorBanner'

type ApiBundle = {
  state: any
  pnl: any
  tradesToday: any
}

function money(v: any) {
  const n = Number(v || 0)
  return `₹${Number.isFinite(n) ? n.toFixed(2) : '0.00'}`
}

function statusBadge(ok: boolean, text: string) {
  return (
    <span className={`inline-flex px-2 py-1 rounded text-xs font-bold ${ok ? 'bg-green-900/30 text-green-300 border border-green-700' : 'bg-red-900/30 text-red-300 border border-red-700'}`}>
      {text}
    </span>
  )
}

export default function PaperTrading() {
  const [bundle, setBundle] = useState<ApiBundle | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<string>('')

  const fetchData = async () => {
    try {
      const [stateRes, pnlRes, tradesRes] = await Promise.all([
        axios.get(`${API_BASE}/api/state`),
        axios.get(`${API_BASE}/api/pnl`),
        axios.get(`${API_BASE}/api/trades/today`).catch((err) => ({ data: { status: 'ERROR', error: err.message, entries: [], exits: [], count: 0 } })),
      ])
      setBundle({ state: stateRes.data, pnl: pnlRes.data || null, tradesToday: tradesRes.data || null })
      setLastRefresh(new Date().toLocaleString())
      setError(null)
    } catch (err: any) {
      console.error('Error fetching paper trading data:', err)
      setError(err.message || 'Failed to fetch paper trading data')
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (error && !bundle) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Paper Trading Console</h2>
        <ErrorBanner endpoint={`${API_BASE}/api/state`} message={error} onRetry={fetchData} />
      </div>
    )
  }

  if (!bundle) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Paper Trading Console</h2>
        <div className="p-6 text-center text-gray-400">Loading paper/analyzer proof...</div>
      </div>
    )
  }

  const state = bundle.state || {}
  const pnl = bundle.pnl || {}
  const tradesToday = bundle.tradesToday || {}
  const positions = Array.isArray(state.positions) ? state.positions : []
  const positionsSource = state.positions_source || 'INTERNAL_UNVERIFIED'
  const dataSource = state.data_source || 'not_ready'
  const brokerConnected = Boolean(state?.broker?.connected)
  const mode = state.mode || 'PAPER'
  const stateVersion = state.state_version || 0
  const liveTradingAllowed = String(state.live_trading_enabled || state.liveTradingEnabled || '0') === '1'
  const analyzerSafe = String(mode).toUpperCase().includes('PAPER') || String(mode).toUpperCase().includes('ANALYZER') || !liveTradingAllowed

  const pnlHistory = (pnl?.history || []).map((item: any) => {
    let timestamp = item.timestamp || item.date || item.time || new Date().toISOString()
    const parsed = new Date(timestamp)
    timestamp = isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString()
    return { ...item, timestamp, total_pnl: Number(item.total_pnl || item.total_unrealized_pnl || 0) }
  }).filter((item: any) => !isNaN(new Date(item.timestamp).getTime()))

  const summary = pnl?.summary || {}
  const totalUnrealized = positions.reduce((sum: number, p: any) => sum + Number(p.unrealized_pnl || 0), 0)
  const totalRealized = Number(summary?.total_realized_pnl || 0)
  const totalPnL = totalUnrealized + totalRealized
  const todayEntries = Array.isArray(tradesToday.entries) ? tradesToday.entries : []
  const todayExits = Array.isArray(tradesToday.exits) ? tradesToday.exits : []

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']
  const isRealData = dataSource === 'REAL' || dataSource === 'real' || dataSource === 'dhan'
  const paperTruthOk = analyzerSafe && !liveTradingAllowed

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start gap-4">
        <div>
          <h2 className="text-3xl font-bold">Paper Trading Console</h2>
          <div className="text-sm text-gray-400 mt-1">
            State Version: {stateVersion} | Positions Source: {positionsSource} | Last Refresh: {lastRefresh || '-'}
          </div>
        </div>
        <button onClick={fetchData} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white font-bold">
          Recheck Paper Proof
        </button>
      </div>

      {error && (
        <div className="bg-yellow-900/20 border border-yellow-700 p-3 rounded-lg text-yellow-300 text-sm">
          Last poll failed but last-good data is still visible: {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Mode Safety</div>
          <div className="mt-2">{statusBadge(paperTruthOk, paperTruthOk ? 'PAPER / ANALYZER SAFE' : 'BLOCKED')}</div>
          <div className="text-xs text-gray-500 mt-2">Live trading flag: {liveTradingAllowed ? 'ON' : 'OFF'}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Broker Data</div>
          <div className="mt-2">{statusBadge(Boolean(brokerConnected), brokerConnected ? 'CONNECTED' : 'NOT CONNECTED')}</div>
          <div className="text-xs text-gray-500 mt-2">Source: {String(dataSource)}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Today Paper Entries</div>
          <div className="text-2xl font-bold mt-1">{todayEntries.length}</div>
          <div className="text-xs text-gray-500 mt-2">From /api/trades/today</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Today Paper Exits</div>
          <div className="text-2xl font-bold mt-1">{todayExits.length}</div>
          <div className="text-xs text-gray-500 mt-2">Closed paper/analyzer records</div>
        </div>
      </div>

      <DataSourceWarning dataSource={dataSource} brokerConnected={brokerConnected} mode={mode} />

      {positionsSource === 'INTERNAL_UNVERIFIED' && positions.length > 0 && (
        <div className="bg-orange-900/20 border border-orange-700 p-3 rounded-lg">
          <div className="text-sm text-orange-300">
            ⚠️ Positions shown are INTERNAL_UNVERIFIED. Treat as paper/analyzer evidence only, not broker reality.
          </div>
        </div>
      )}

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Open Paper Positions ({positions.length})</h3>
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
                  <th className="text-left p-2">Action Safety</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos: any, idx: number) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-2">{pos.position_id || 'N/A'}</td>
                    <td className="p-2">{pos.symbol || pos.underlying || 'N/A'}</td>
                    <td className="text-right p-2">{pos.qty || pos.quantity || 0}</td>
                    <td className="text-right p-2">{money(pos.entry_price)}</td>
                    <td className="text-right p-2">{money(pos.current_price ?? pos.entry_price)}</td>
                    <td className={`text-right p-2 ${Number(pos.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(pos.unrealized_pnl)}</td>
                    <td className="text-right p-2 text-xs">SL: {money(pos.stop_loss)}<br/>TG: {money(pos.target)}</td>
                    <td className="text-left p-2 text-xs text-gray-400">
                      Signal: {pos.signal_source || pos.strategy || 'N/A'}<br/>
                      {pos.entry_time ? `Entry: ${new Date(pos.entry_time).toLocaleString()}` : ''}
                      {pos.confidence ? ` | Conf: ${(Number(pos.confidence) * 100).toFixed(0)}%` : ''}
                    </td>
                    <td className="text-left p-2 text-xs text-yellow-300">Read-only proof. No broker/position close route called from paper UI.</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="bg-gray-900/50 border border-gray-700 p-6 rounded">
            <div className="font-bold text-gray-200">No open paper positions</div>
            <div className="text-sm text-gray-400 mt-2">Reason: paper engine has no open simulated position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.</div>
          </div>
        )}
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Today Paper Trade Proof</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <div className="font-bold mb-2">Entries ({todayEntries.length})</div>
            <pre className="bg-gray-900 p-3 rounded text-xs overflow-auto max-h-64">{JSON.stringify(todayEntries.slice(0, 20), null, 2)}</pre>
          </div>
          <div>
            <div className="font-bold mb-2">Exits ({todayExits.length})</div>
            <pre className="bg-gray-900 p-3 rounded text-xs overflow-auto max-h-64">{JSON.stringify(todayExits.slice(0, 20), null, 2)}</pre>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Equity Curve</h3>
          {pnlHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={pnlHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tickFormatter={(v) => new Date(v).toLocaleTimeString()} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="total_pnl" stroke="#8884d8" name="Total PnL" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="bg-gray-900/50 border border-gray-700 p-6 rounded"><div className="font-bold text-gray-200">No PnL curve yet</div><div className="text-sm text-gray-400 mt-2">Chart appears after paper engine records history.</div></div>
          )}
        </div>

        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">PnL Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between"><span>Total PnL:</span><span className={`font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(totalPnL)}</span></div>
            <div className="flex justify-between"><span>Unrealized:</span><span className={`${totalUnrealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(totalUnrealized)}</span></div>
            <div className="flex justify-between"><span>Realized:</span><span className={`${totalRealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(totalRealized)}</span></div>
            <div className="flex justify-between"><span>Open Positions:</span><span>{positions.length}</span></div>
            <div className="flex justify-between"><span>Today Entries:</span><span>{todayEntries.length}</span></div>
            <div className="flex justify-between"><span>Today Exits:</span><span>{todayExits.length}</span></div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Win Rate</h3>
        {summary.total_trades > 0 ? (
          <div className="space-y-4">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={[{ name: 'Winning', value: summary.winning_trades || 0 }, { name: 'Losing', value: summary.losing_trades || 0 }]} cx="50%" cy="50%" labelLine={false} label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`} outerRadius={80} fill="#8884d8" dataKey="value">
                  {[0, 1].map((_entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
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

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Risk Panel</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><div className="text-sm text-gray-400">Max Positions</div><div className="text-2xl font-bold">5</div><div className="text-xs text-gray-500">Current: {positions.length}</div></div>
          <div><div className="text-sm text-gray-400">Total Paper Exposure</div><div className="text-2xl font-bold">{money(positions.reduce((sum: number, p: any) => sum + (Number(p.entry_price || 0) * Number(p.qty || 0)), 0))}</div></div>
          <div><div className="text-sm text-gray-400">Live Order Safety</div><div className="text-2xl font-bold text-green-400">BLOCKED</div><div className="text-xs text-gray-500">Paper UI does not call broker/order close endpoints.</div></div>
        </div>
      </div>
    </div>
  )
}
