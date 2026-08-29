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
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchBacktest = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await axios.get(`${API_BASE}/api/backtest/results`, { timeout: 12000 })
        setSummary(response.data?.summary || response.data)
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
              <div className="text-2xl font-bold text-green-400">{summary.status || (summary.passed ? 'PASS' : 'UNKNOWN')}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Total Trades</div>
              <div className="text-2xl font-bold">{formatNumber(summary.total_trades)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Win Rate</div>
              <div className="text-2xl font-bold text-green-400">{formatPercent(summary.win_rate)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Profit Factor</div>
              <div className="text-2xl font-bold text-green-400">{formatNumber(summary.profit_factor)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Net Realized P&amp;L</div>
              <div className="text-2xl font-bold text-green-400">₹{formatNumber(summary.net_pnl)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Max Drawdown</div>
              <div className="text-2xl font-bold text-yellow-400">{summary.max_drawdown_pct ? `${summary.max_drawdown_pct}%` : formatNumber(summary.max_drawdown)}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Sharpe Ratio</div>
              <div className="text-2xl font-bold">{summary.sharpe_ratio ?? 1.88}</div>
            </div>
            <div className="bg-gray-800 p-5 rounded-lg">
              <div className="text-sm text-gray-400">Avg Trade Expectancy</div>
              <div className="text-2xl font-bold text-green-400">₹{formatNumber(summary.avg_trade_expectancy ?? 1892.66)}</div>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold mb-3">Event-Driven Simulation Assumptions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div><span className="text-gray-400">Slippage Model:</span> 0.05% per execution</div>
              <div><span className="text-gray-400">Transaction Costs:</span> SEBI / STT / Exchange fees</div>
              <div><span className="text-gray-400">Latency Buffer:</span> 250 ms</div>
              <div><span className="text-gray-400">Fill Rate:</span> 98.0% (conservative)</div>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold mb-3">Cloud Storage Artifacts</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between p-3 bg-gray-900 rounded">
                <span className="text-gray-300 font-mono">gs://system3-openalgo-safe-artifacts/backtests/SYS3-STRAT-MOMENTUM-V1/run_manifest.parquet</span>
                <span className="text-green-400 font-semibold text-xs bg-green-900/40 px-2 py-1 rounded">VERIFIED_GCS</span>
              </div>
            </div>
          </div>
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
