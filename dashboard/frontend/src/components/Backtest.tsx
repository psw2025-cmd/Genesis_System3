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
  verification_status?: string
  reason_if_unverified?: string
  [key: string]: unknown
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
  const [reason, setReason] = useState('No independently verified historical backtest')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchBacktest = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await axios.get(`${API_BASE}/api/backtest/results`, { timeout: 12000 })
        const payload = response.data || {}
        const isVerified = payload.passed === true && payload.status === 'PASS' && payload.verification_status === 'VERIFIED'
        setReason(payload.reason_if_unverified || 'No independently verified historical backtest')
        setSummary({ ...(isVerified ? payload.summary || {} : {}), status: isVerified ? 'PASS' : 'NOT VERIFIED', passed: isVerified })
      } catch (err: any) {
        setSummary(null)
        setError(err?.message || 'Backtest data pending')
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
            Production readiness requires recent evidence from /api/backtest/results.
          </p>
        </div>
      )}

      {summary && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Simulation Status</div>
              <div className="text-2xl font-bold text-yellow-400">{summary.status || (summary.passed ? 'PASS' : 'UNKNOWN')}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Total Trades</div>
              <div className="text-2xl font-bold">{formatNumber(summary.total_trades)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Win Rate</div>
              <div className="text-2xl font-bold text-gray-200">{summary.passed ? formatPercent(summary.win_rate) : "PENDING"}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Profit Factor</div>
              <div className="text-2xl font-bold text-gray-200">{summary.passed ? formatNumber(summary.profit_factor) : "PENDING"}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Net Realized P&amp;L</div>
              <div className="text-2xl font-bold text-gray-200">{summary.passed ? `₹${formatNumber(summary.net_pnl)}` : "PENDING"}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Max Drawdown</div>
              <div className="text-2xl font-bold text-yellow-400">{summary.max_drawdown_pct ? `${summary.max_drawdown_pct}%` : formatNumber(summary.max_drawdown)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Sharpe Ratio</div>
              <div className="text-2xl font-bold">{summary.sharpe_ratio == null ? 'PENDING' : String(summary.sharpe_ratio)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Avg Trade Expectancy</div>
              <div className="text-2xl font-bold text-green-400">{summary.avg_trade_expectancy == null ? 'PENDING' : `₹${formatNumber(summary.avg_trade_expectancy)}`}</div>
            </div>
          </div>

          {!summary.passed && (
            <div className="bg-yellow-900/40 border border-yellow-700 p-6 rounded-lg" role="status">
              <h3 className="font-bold text-yellow-200">Historical backtest NOT VERIFIED</h3>
              <p className="text-yellow-100 mt-2">{reason}</p>
              <p className="text-yellow-100 mt-2">No certified paper P&L, execution assumptions, trade history, chart curve, or cloud artifacts.</p>
            </div>
          )}
        </>
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
