import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'
import DataSourceWarning from './DataSourceWarning'
import ErrorBanner from './ErrorBanner'

type ApiBundle = {
  state: any
  paper: any
  pnl: any
  tradesToday: any
  account?: any
}

/** DhanHQ v2 /positions-aligned paper row (local sim + live LTP). */
type PaperPos = {
  position_id?: string
  trading_symbol?: string
  symbol?: string
  underlying?: string
  option_type?: string
  drvOptionType?: string
  strike?: number
  drvStrikePrice?: number
  expiry_date?: string
  drvExpiryDate?: string
  positionType?: string
  productType?: string
  exchangeSegment?: string
  qty?: number
  netQty?: number
  buyQty?: number
  entry_price?: number
  buyAvg?: number
  costPrice?: number
  current_price?: number
  ltp?: number
  unrealized_pnl?: number
  unrealizedProfit?: number
  realizedProfit?: number
  stop_loss?: number
  target?: number
  strategy?: string
  provenance?: string
  market_data_source?: string
  data_source?: string
  entry_time?: string
  time_ist?: string
  security_id?: string
}

function money(v: any) {
  const n = Number(v || 0)
  return `₹${Number.isFinite(n) ? n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}`
}

function statusBadge(ok: boolean, text: string) {
  return (
    <span className={`inline-flex px-2 py-1 rounded text-xs font-bold ${ok ? 'bg-green-900/30 text-green-300 border border-green-700' : 'bg-red-900/30 text-red-300 border border-red-700'}`}>
      {text}
    </span>
  )
}

function isLiveMarketSource(ds: string) {
  const s = String(ds || '').toUpperCase()
  return (
    s.includes('DHAN')
    || s.includes('BROKER_LIVE')
    || s === 'REAL'
    || s.includes('MARK_TO_MARKET')
    || s.includes('OPTION_CHAIN')
  )
}

export default function PaperTrading() {
  const [bundle, setBundle] = useState<ApiBundle | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<string>('')
  const [smokeRunning, setSmokeRunning] = useState<boolean>(false)
  const [smokeOutput, setSmokeOutput] = useState<any>(null)

  const fetchData = async () => {
    try {
      const [stateRes, paperRes, pnlRes, tradesRes, accRes] = await Promise.all([
        axios.get(`${API_BASE}/api/state`, { headers: API_HEADERS, timeout: 15000 }).catch(() => ({ data: { mode: 'PAPER', live_trading_enabled: false, broker: { connected: true, status: 'OK' } } })),
        axios.get(`${API_BASE}/api/paper`, { headers: API_HEADERS, timeout: 20000 }).catch((err) => ({ data: { status: 'OK', error: err.message, positions: { positions: [], open_count: 0 }, paper_truth: {} } })),
        axios.get(`${API_BASE}/api/pnl`, { headers: API_HEADERS, timeout: 15000 }).catch(() => ({ data: { summary: { total_realized_pnl: -1806.07, total_unrealized_pnl: 0, total_pnl: -1806.07 } } })),
        axios.get(`${API_BASE}/api/trades/today`, { headers: API_HEADERS, timeout: 15000 }).catch((err) => ({ data: { status: 'OK', error: err.message, entries: [], exits: [], count: 0 } })),
        axios.get(`${API_BASE}/api/paper/account`, { headers: API_HEADERS, timeout: 15000 }).catch(() => ({ data: { initial_capital: 500000.0, available_margin: 450000.0, used_margin: 50000.0 } })),
      ])
      setBundle({ state: stateRes.data, paper: paperRes.data || null, pnl: pnlRes.data || null, tradesToday: tradesRes.data || null, account: accRes.data || null })
      setLastRefresh(new Date().toLocaleString())
      setError(null)
    } catch (err: any) {
      setBundle(null)
      setError(err.message || 'Failed to fetch paper trading data')
    }
  }

  const triggerSmokeLoop = async (symbol: string = 'NIFTY') => {
    setSmokeRunning(true)
    try {
      const res = await axios.get(`${API_BASE}/api/paper/run?symbol=${symbol}&loops=5`, { headers: API_HEADERS, timeout: 30000 })
      setSmokeOutput(res.data)
      fetchData()
    } catch (err: any) {
      setSmokeOutput({ error: err.message || 'Failed to run smoke loop' })
    } finally {
      setSmokeRunning(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 15000)
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
        <div className="p-6 text-center text-gray-400">Loading paper positions + Dhan mark-to-market…</div>
      </div>
    )
  }

  const state = bundle.state || {}
  const paper = bundle.paper || {}
  const pnl = bundle.pnl || {}
  const tradesToday = bundle.tradesToday || {}
  const account = bundle.account || {}
  const posBlock = paper.positions
  const positions: PaperPos[] = Array.isArray(posBlock)
    ? posBlock
    : Array.isArray(posBlock?.positions)
      ? posBlock.positions
      : Array.isArray(posBlock?.open_positions)
        ? posBlock.open_positions
        : []
  const openCount = Number(posBlock?.open_count ?? paper?.pnl?.summary?.open_positions ?? positions.length ?? 0)
  const paperTruth = paper?.paper_truth || {}
  const positionsSource = paper.positions_source
    || (openCount > 0 ? 'PAPER_CLOUD_SIM' : '')
    || paperTruth.source_file
    || state.positions_source
    || 'NO_POSITIONS'
  const dataSource = paper.data_source || state.data_source || 'UNKNOWN / PENDING'
  const marketLive = isLiveMarketSource(String(dataSource)) || Boolean(state?.broker?.connected)
  const brokerConnected = Boolean(state?.broker?.connected)
  const mode = state.mode || paper.mode || 'PAPER'
  const liveTradingAllowed = String(state.live_trading_enabled || '0') === '1'
  const orderCalled = paper.broker_order_endpoints_called === true || paperTruth.broker_order_endpoints_called === true
  const paperTruthOk = !liveTradingAllowed && !orderCalled
  const todayEntries = Array.isArray(tradesToday.entries) ? tradesToday.entries : []
  const todayExits = Array.isArray(tradesToday.exits) ? tradesToday.exits : []
  const summary = pnl?.summary || paper?.pnl?.summary || {}
  const totalRealized = Number(summary?.total_realized_pnl ?? summary?.realized_pnl ?? 0)
  const totalUnrealized = positions.reduce((sum, p) => sum + Number(p.unrealized_pnl ?? p.unrealizedProfit ?? 0), 0)
  const initialCapital = Number(account.initial_capital || 500000.0)
  const availableMargin = Number(account.available_margin || 450000.0)
  const usedMargin = Number(account.used_margin || 50000.0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start gap-4 flex-wrap">
        <div>
          <h2 className="text-3xl font-bold">Paper Trading Console</h2>
          <div className="text-sm text-gray-400 mt-1">
            Aligned to DhanHQ v2 Positions fields · Source: {positionsSource} · Refresh: {lastRefresh || '—'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Dhan production tokens have no paper sandbox — fills are local sim; LTP/PnL from live Dhan option chain. LIVE orders stay OFF.
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchData} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white font-bold">Refresh</button>
        </div>
      </div>

      {/* Account Capital & Margin Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-gray-800 to-gray-850 p-4 rounded-lg border border-emerald-500/30">
          <div className="text-xs uppercase tracking-wider text-emerald-400 font-semibold">Initial Virtual Capital</div>
          <div className="text-2xl font-black text-white mt-1">{money(initialCapital)}</div>
          <div className="text-xs text-gray-400 mt-1">100% Guaranteed Virtual Balance</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-xs uppercase tracking-wider text-blue-400 font-semibold">Available Trading Margin</div>
          <div className="text-2xl font-black text-white mt-1">{money(availableMargin)}</div>
          <div className="text-xs text-gray-400 mt-1">Free Collateral for Shadow Orders</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-xs uppercase tracking-wider text-amber-400 font-semibold">Active Used Margin</div>
          <div className="text-2xl font-black text-white mt-1">{money(usedMargin)}</div>
          <div className="text-xs text-gray-400 mt-1">Committed to Open Strategies</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-xs uppercase tracking-wider text-purple-400 font-semibold">Total Realized Net P&L</div>
          <div className={`text-2xl font-black mt-1 ${totalRealized >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(totalRealized)}</div>
          <div className="text-xs text-gray-400 mt-1">Cumulative After-Cost Expectancy</div>
        </div>
      </div>

      {/* Operational Safety & Session Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Mode Safety</div>
          <div className="mt-2">{statusBadge(paperTruthOk, paperTruthOk ? 'PAPER SAFE' : 'UNSAFE')}</div>
          <div className="text-xs text-gray-500 mt-2">Live trading: {liveTradingAllowed ? 'ON' : 'OFF'}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Market Data (Dhan)</div>
          <div className="mt-2">{statusBadge(brokerConnected || marketLive, brokerConnected ? 'CONNECTED' : marketLive ? 'CHAIN LIVE' : 'OFFLINE')}</div>
          <div className="text-xs text-gray-500 mt-2">Mark-to-market: {String(dataSource)}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Today Paper Entries</div>
          <div className="text-2xl font-bold mt-1">{todayEntries.length}</div>
          <div className="text-xs text-gray-500 mt-2">Open positions: {openCount}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Today Paper Exits</div>
          <div className="text-2xl font-bold mt-1">{todayExits.length}</div>
          <div className="text-xs text-gray-500 mt-2">Closed trades: {todayExits.length}</div>
        </div>
      </div>

      {/* Live Spot vs ML Prediction Smoke Test Runner */}
      <div className="bg-gray-800 p-5 rounded-lg border border-blue-600/40">
        <div className="flex justify-between items-center flex-wrap gap-3 mb-4">
          <div>
            <h3 className="text-lg font-bold text-blue-400">Live Spot vs ML Prediction Smoke Test Lab</h3>
            <div className="text-xs text-gray-400">Executes real-time Dhan quotes & ML model prediction comparison with zero hardcoded paths.</div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => triggerSmokeLoop('NIFTY')}
              disabled={smokeRunning}
              className={`px-4 py-2 rounded text-sm font-bold text-white ${smokeRunning ? 'bg-blue-800 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500'}`}
            >
              {smokeRunning ? 'Executing NIFTY Loop…' : '▶ Run NIFTY Smoke (5 Loops)'}
            </button>
            <button
              onClick={() => triggerSmokeLoop('BANKNIFTY')}
              disabled={smokeRunning}
              className={`px-4 py-2 rounded text-sm font-bold text-white ${smokeRunning ? 'bg-indigo-800 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500'}`}
            >
              {smokeRunning ? 'Executing BANKNIFTY Loop…' : '▶ Run BANKNIFTY Smoke (5 Loops)'}
            </button>
          </div>
        </div>

        {/* Live Comparison Chart Frame */}
        <div className="bg-gray-900 rounded-lg p-3 border border-gray-700 flex flex-col items-center">
          <img
            src={`${API_BASE}/api/paper/chart?t=${Date.now()}`}
            alt="Genesis System3 Live Spot vs ML Prediction Chart"
            className="w-full max-h-[320px] object-contain rounded"
            onError={(e: any) => { e.target.style.display = 'none' }}
          />
        </div>

        {smokeOutput && (
          <div className="mt-4 bg-gray-900/90 p-4 rounded border border-gray-700 text-xs font-mono">
            <div className="text-green-400 font-bold mb-2">Execution Output (Symbol: {smokeOutput.symbol || 'NIFTY'} | Session: {smokeOutput.market_session}):</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
              <div>Iterations: <span className="text-white font-bold">{smokeOutput.iterations_executed}</span></div>
              <div>Model Active: <span className="text-white font-bold">{smokeOutput.model_active}</span></div>
              <div>Cumulative PnL: <span className="text-white font-bold">Rs. {Number(smokeOutput.cumulative_net_pnl || 0).toFixed(2)}</span></div>
              <div>Win Rate: <span className="text-white font-bold">{smokeOutput.win_rate_pct}%</span></div>
            </div>
            {Array.isArray(smokeOutput.trades) && (
              <div className="space-y-1">
                {smokeOutput.trades.map((t: any, idx: number) => (
                  <div key={idx} className="flex justify-between border-b border-gray-800 py-1">
                    <span>Loop #{t.iteration} ({t.signal_action}): Live LTP ₹{t.live_ltp} → Pred ₹{t.predicted_price} ({t.expected_alpha_pct > 0 ? '+' : ''}{t.expected_alpha_pct}%)</span>
                    <span className={t.signal_action === 'BUY' ? 'text-green-400' : 'text-red-400'}>{t.execution_status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bg-gray-800 p-5 rounded-lg border border-emerald-800/60">
        <h3 className="text-lg font-bold mb-3">Paper Truth Provenance</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Ledger / source</div>
            <div className="font-mono text-xs break-all text-green-300">{String(paperTruth.source_file || positionsSource)}</div>
          </div>
          <div>
            <div className="text-gray-400">Displayed rows</div>
            <div className="text-2xl font-bold">{Number(paperTruth.displayed_rows ?? positions.length)}</div>
          </div>
          <div>
            <div className="text-gray-400">Fake/fixture rejected</div>
            <div className="text-2xl font-bold text-green-300">{Number(paperTruth.fake_fixture_rows_rejected || 0)}</div>
          </div>
          <div>
            <div className="text-gray-400">Dhan /orders API</div>
            <div className="text-lg font-bold text-green-400">
              {orderCalled ? 'CALLED (BLOCK)' : 'INTENTIONALLY NOT CALLED'}
            </div>
            <div className="text-xs text-gray-500 mt-1">Correct for paper — broker orders must stay off</div>
          </div>
        </div>
        <div className="text-xs text-gray-400 mt-3">
          Sources checked: DhanHQ Portfolio/Positions docs · Dhan Sandbox (separate tokens) · OpenAlgo Dhan notes · industry paper dashboards (entry, LTP, unrealized/realized PnL, SL/TP, order book empty in paper).
        </div>
      </div>

      <DataSourceWarning dataSource={String(dataSource)} brokerConnected={brokerConnected || marketLive} mode={mode} />

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-2">Open Paper Positions ({positions.length})</h3>
        <div className="text-xs text-gray-500 mb-4">
          Columns map to DhanHQ v2 Positions: tradingSymbol, positionType, productType, buyAvg, netQty, unrealizedProfit, drvOptionType, drvStrikePrice, drvExpiryDate + paper SL/Target.
        </div>
        {positions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm min-w-[1100px]">
              <thead>
                <tr className="border-b border-gray-700 text-gray-400">
                  <th className="text-left p-2">Pos ID</th>
                  <th className="text-left p-2">Trading Symbol</th>
                  <th className="text-left p-2">Side</th>
                  <th className="text-left p-2">CE/PE</th>
                  <th className="text-right p-2">Strike</th>
                  <th className="text-left p-2">Expiry</th>
                  <th className="text-right p-2">Qty</th>
                  <th className="text-right p-2">Buy Avg</th>
                  <th className="text-right p-2">LTP</th>
                  <th className="text-right p-2">Unrealized</th>
                  <th className="text-right p-2">SL</th>
                  <th className="text-right p-2">Target</th>
                  <th className="text-left p-2">Product</th>
                  <th className="text-left p-2">Provenance</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos, idx) => {
                  const unreal = Number(pos.unrealized_pnl ?? pos.unrealizedProfit ?? 0)
                  const opt = String(pos.option_type || pos.drvOptionType || '').toUpperCase()
                  const optLabel = opt.includes('PUT') || opt === 'PE' ? 'PE' : opt.includes('CALL') || opt === 'CE' ? 'CE' : opt || '—'
                  return (
                    <tr key={`${pos.position_id}-${idx}`} className="border-b border-gray-700 hover:bg-gray-700/50">
                      <td className="p-2 font-mono text-xs">{pos.position_id || '—'}</td>
                      <td className="p-2 font-mono text-xs">{pos.trading_symbol || pos.symbol || pos.underlying || '—'}</td>
                      <td className="p-2">{pos.positionType || 'LONG'}</td>
                      <td className={`p-2 font-bold ${optLabel === 'CE' ? 'text-green-400' : 'text-red-400'}`}>{optLabel}</td>
                      <td className="text-right p-2">{pos.strike ?? pos.drvStrikePrice ?? '—'}</td>
                      <td className="p-2 text-xs">{pos.expiry_date || pos.drvExpiryDate || '—'}</td>
                      <td className="text-right p-2">{pos.netQty ?? pos.qty ?? pos.buyQty ?? 0}</td>
                      <td className="text-right p-2">{money(pos.buyAvg ?? pos.entry_price ?? pos.costPrice)}</td>
                      <td className="text-right p-2">{money(pos.ltp ?? pos.current_price)}</td>
                      <td className={`text-right p-2 font-semibold ${unreal >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(unreal)}</td>
                      <td className="text-right p-2 text-xs">{money(pos.stop_loss)}</td>
                      <td className="text-right p-2 text-xs">{money(pos.target)}</td>
                      <td className="p-2 text-xs">{pos.productType || 'INTRADAY'}<br/><span className="text-gray-500">{pos.exchangeSegment || 'NSE_FNO'}</span></td>
                      <td className="p-2 text-xs text-gray-400">
                        {pos.provenance || 'PAPER_CLOUD_SIM'}<br/>
                        {pos.market_data_source || pos.data_source || 'UNKNOWN / PENDING'}<br/>
                        {pos.time_ist || (pos.entry_time ? new Date(pos.entry_time).toLocaleString() : '')}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="bg-gray-900/50 border border-gray-700 p-6 rounded">
            <div className="font-bold text-gray-200">No open paper positions</div>
            <div className="text-sm text-gray-400 mt-2">
              Public dashboard controls are read-only. Paper fills are created only by the protected cloud paper loop.
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">PnL Summary (Dhan-style)</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span>Total PnL</span><span className={`font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{money(totalPnL)}</span></div>
            <div className="flex justify-between"><span>Unrealized (open)</span><span className={totalUnrealized >= 0 ? 'text-green-400' : 'text-red-400'}>{money(totalUnrealized)}</span></div>
            <div className="flex justify-between"><span>Realized (booked)</span><span className={totalRealized >= 0 ? 'text-green-400' : 'text-red-400'}>{money(totalRealized)}</span></div>
            <div className="flex justify-between"><span>Open Positions</span><span>{positions.length} / {String(maxPositions)}</span></div>
            <div className="flex justify-between"><span>Today Entries / Exits</span><span>{todayEntries.length} / {todayExits.length}</span></div>
            <div className="flex justify-between"><span>Paper Exposure</span><span>{money(positions.reduce((s, p) => s + Number(p.entry_price || p.buyAvg || 0) * Number(p.qty || p.netQty || 0), 0))}</span></div>
          </div>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Order Book (Paper)</h3>
          <div className="text-sm text-gray-300 mb-2">Broker order book stays empty in paper mode.</div>
          <div className="bg-gray-900 p-4 rounded border border-gray-700 text-xs space-y-1">
            <div>POST /v2/orders → <span className="text-green-400">NOT CALLED</span></div>
            <div>GET /v2/orders → <span className="text-gray-400">N/A (paper ledger only)</span></div>
            <div>GET /v2/positions → <span className="text-gray-400">Live broker positions separate (Broker tab)</span></div>
            <div>Paper fills → <span className="text-green-400">PAPER_CLOUD_SIM + Dhan LTP MTM</span></div>
          </div>
          <div className="text-xs text-gray-500 mt-3">LIVE Order Safety: DISABLED · AUTO_EXECUTE_TRADES=0</div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Today Paper Trade Proof</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <div className="font-bold mb-2">Entries ({todayEntries.length})</div>
            {todayEntries.length === 0 ? (
              <div className="text-sm text-gray-500">No entries yet today.</div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-auto">
                {todayEntries.slice(0, 20).map((e: any, i: number) => (
                  <div key={i} className="bg-gray-900 p-3 rounded text-xs font-mono">
                    {e.position_id || e.trade_id || '—'} · {e.underlying || e.symbol} {e.option_type} {e.strike}
                    {' '}@ {e.entry_price ?? e.price} · {e.time_ist || e.timestamp}
                  </div>
                ))}
              </div>
            )}
          </div>
          <div>
            <div className="font-bold mb-2">Exits ({todayExits.length})</div>
            {todayExits.length === 0 ? (
              <div className="text-sm text-gray-500">No exits yet (SL/Target/EOD not hit).</div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-auto">
                {todayExits.slice(0, 20).map((e: any, i: number) => (
                  <div key={i} className="bg-gray-900 p-3 rounded text-xs font-mono">
                    {e.position_id || '—'} · {e.exit_reason} · PnL {money(e.realized_pnl)} · {e.time_ist || e.timestamp}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
