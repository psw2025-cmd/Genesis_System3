import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

type BacktestSummary = {
  status?: string
  passed?: boolean
  total_trades?: number
  win_rate?: number
  profit_factor?: number
  net_pnl?: number
  max_drawdown?: number
  generated_at?: string
  message?: string
  [key: string]: any
}

const formatPercent = (value: unknown): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return `${(value * 100).toFixed(2)}%`
}

const formatNumber = (value: unknown): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

export default function Backtest() {
  const [summary, setSummary] = useState<BacktestSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchBacktest = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await axios.get(`${API_BASE}/api/backtest`, { timeout: 7000 })
        setSummary(response.data?.summary || response.data)
      } catch (err: any) {
        setSummary(null)
        setError(err?.message || 'Backtest endpoint unavailable')
      } finally {
        setLoading(false)
      }
    }

    fetchBacktest()
    const interval = setInterval(fetchBacktest, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">Backtest Readiness</h2>
        <p className="text-gray-400 mt-2">
          Read-only backtest proof panel for analyzer/paper validation. This panel does not place trades.
        </p>
      </div>

      {loading && (
        <div className="bg-gray-800 p-6 rounded-lg text-gray-300">Loading backtest proof...</div>
      )}

      {error && (
        <div className="bg-yellow-900/40 border border-yellow-700 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-2">Backtest endpoint not proven</h3>
          <p className="text-yellow-200">{error}</p>
          <p className="text-sm text-yellow-100 mt-3">
            Dashboard route exists, but production readiness requires backend /api/backtest proof.
          </p>
        </div>
      )}

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-800 p-5 rounded-lg">
            <div className="text-sm text-gray-400">Status</div>
            <div className="text-2xl font-bold">{summary.status || (summary.passed ? 'PASS' : 'UNKNOWN')}</div>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg">
            <div className="text-sm text-gray-400">Total Trades</div>
            <div className="text-2xl font-bold">{formatNumber(summary.total_trades)}</div>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg">
            <div className="text-sm text-gray-400">Win Rate</div>
            <div className="text-2xl font-bold">{formatPercent(summary.win_rate)}</div>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg">
            <div className="text-sm text-gray-400">Profit Factor</div>
            <div className="text-2xl font-bold">{formatNumber(summary.profit_factor)}</div>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg">
            <div className="text-sm text-gray-400">Net P&amp;L</div>
            <div className="text-2xl font-bold">{formatNumber(summary.net_pnl)}</div>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg">
            <div className="text-sm text-gray-400">Max Drawdown</div>
            <div className="text-2xl font-bold">{formatNumber(summary.max_drawdown)}</div>
          </div>
        </div>
      )}

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-3">Readiness Rule</h3>
        <p className="text-gray-300">
          Full production grade requires recent walk-forward backtest proof, analyzer-only lifecycle proof,
          dashboard/browser proof, and broker/live trading disabled until multi-week paper stability is verified.
        </p>
      </div>
    </div>
  )
}
