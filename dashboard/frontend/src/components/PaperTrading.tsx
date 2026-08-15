import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'
import DataSourceWarning from './DataSourceWarning'
import ErrorBanner from './ErrorBanner'

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
  return `₹${Number.isFinite(n) ? n.toFixed(2) : '0.00'}`
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
  return s.includes('DHAN') || s.includes('BROKER_LIVE') || s === 'REAL' || s.includes('MARK_TO_MARKET') || s.includes('OPTION_CHAIN')
}

export default function PaperTrading() {
  const [paper, setPaper] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<string>('')

  const fetchData = async () => {
    try {
      // One self-contained truth endpoint.  Do not make Paper rendering depend
      // on /state + /pnl + /trades fan-out or on any local Cloud Run file.
      const response = await axios.get(`${API_BASE}/api/paper`, {
        headers: API_HEADERS,
        timeout: 12000,
        params: { _ts: Date.now() },
      })
      const data = response.data || {}
      if (!['ok', 'EMPTY'].includes(String(data.status || ''))) {
        throw new Error(`Durable paper ledger returned ${String(data.status || 'UNKNOWN')}`)
      }
      setPaper(data)
      setLastRefresh(new Date().toLocaleString())
      setError(null)
    } catch (err: any) {
      setPaper(null)
      setError(err?.response?.data?.paper_truth?.error_type || err?.message || 'Durable paper ledger unavailable')
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 15000)
    return () => clearInterval(interval)
  }, [])

  if (error && !paper) {
    return (
      <div className="space-y-6" data-paper-proof-state="unavailable">
        <h2 className="text-3xl font-bold">Paper Trading Console</h2>
        <div className="bg-red-950/30 border border-red-800 rounded p-4 text-sm text-red-200">
          Durable paper ledger unavailable. The dashboard will not substitute zeros, fixtures, or container-local files.
        </div>
        <ErrorBanner endpoint={`${API_BASE}/api/paper`} message={error} onRetry={fetchData} />
      </div>
    )
  }

  if (!paper) {
    return (
      <div className="space-y-6" data-paper-proof-state="loading">
        <h2 className="text-3xl font-bold">Paper Trading Console</h2>
        <div className="p-6 text-center text-gray-400">Loading durable Firestore paper ledger…</div>
      </div>
    )
  }

  const posBlock = paper.positions || {}
  const positions: PaperPos[] = Array.isArray(posBlock)
    ? posBlock
    : Array.isArray(posBlock?.positions)
      ? posBlock.positions
      : Array.isArray(posBlock?.open_positions)
        ? posBlock.open_positions
        : []
  const openCount = Number(posBlock?.open_count ?? positions.length ?? 0)
  const paperTruth = paper?.paper_truth || {}
  const positionsSource = paper.positions_source || paperTruth.ledger_source || 'FIRESTORE_PAPER_LEDGER'
  const dataSource = paper.data_source || 'UNKNOWN / PENDING'
  const marketLive = isLiveMarketSource(String(dataSource))
  const brokerConnected = marketLive
  const mode = paper.mode || 'PAPER'
  const liveTradingAllowed = paper.live_trading_enabled === true
  const orderCalled = paper.broker_order_endpoints_called === true || paperTruth.broker_order_endpoints_called === true
  const durableLedger = paperTruth.durable === true && String(positionsSource).includes('FIRESTORE_PAPER_LEDGER')
  const paperTruthOk = durableLedger && !liveTradingAllowed && !orderCalled
  const trades = paper?.trades || {}
  const todayEntries = Array.isArray(trades.entries) ? trades.entries : []
  const todayExits = Array.isArray(trades.exits) ? trades.exits : []
  const summary = paper?.pnl?.summary || {}
  const totalRealized = Number(summary?.total_realized_pnl ?? summary?.realized_pnl ?? 0)
  const totalUnrealized = Number(summary?.total_unrealized_pnl ?? positions.reduce((sum, p) => sum + Number(p.unrealized_pnl ?? p.unrealizedProfit ?? 0), 0))
  const totalPnL = Number(summary?.total_pnl ?? (totalRealized + totalUnrealized))
  const maxPositions = 3
  const ledgerVersion = Number(paperTruth.ledger_version || 0)
  const settledStatus = String(paper.status) === 'EMPTY' ? 'EMPTY / READY' : 'READY'

  return (
    <div className="space-y-6" data-paper-proof-state="settled" data-paper-ledger-source="FIRESTORE_PAPER_LEDGER">
      <div className="flex justify-between items-start gap-4 flex-wrap">
        <div>
          <h2 className="text-3xl font-bold">Paper Trading Console</h2>
          <div className="text-sm text-gray-400 mt-1">
            Durable source: FIRESTORE_PAPER_LEDGER · Ledger v{ledgerVersion} · {settledStatus} · Refresh: {lastRefresh || '—'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Paper fills are simulated by a bounded Cloud Run Job; Dhan option-chain LTP marks PnL. LIVE broker orders stay OFF.
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchData} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white font-bold">Refresh</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Mode Safety</div>
          <div className="mt-2">{statusBadge(paperTruthOk, paperTruthOk ? 'PAPER SAFE' : 'TRUTH BLOCKED')}</div>
          <div className="text-xs text-gray-500 mt-2">Live trading: {liveTradingAllowed ? 'ON' : 'OFF'}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Market Data</div>
          <div className="mt-2">{statusBadge(marketLive || String(dataSource).includes('MARKET_CLOSED'), marketLive ? 'DHAN LIVE' : 'DURABLE / CLOSED')}</div>
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
          <div className="text-xs text-gray-500 mt-2">Realized: {money(totalRealized)}</div>
        </div>
      </div>

      <div className="bg-gray-800 p-5 rounded-lg border border-emerald-800/60">
        <h3 className="text-lg font-bold mb-3">Paper Truth Provenance</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Ledger / source</div>
            <div className="font-mono text-xs break-all text-green-300">FIRESTORE_PAPER_LEDGER</div>
          </div>
          <div>
            <div className="text-gray-400">Ledger version / rows</div>
            <div className="text-lg font-bold">v{ledgerVersion} · {Number(paperTruth.displayed_rows ?? positions.length)}</div>
          </div>
          <div>
            <div className="text-gray-400">Durability / updated</div>
            <div className="text-sm font-bold text-green-300">{paperTruth.durable ? 'DURABLE' : 'BLOCKED'}</div>
            <div className="text-xs text-gray-500 break-all">{paperTruth.firestore_updated_at_utc || paperTruth.updated_at_utc || 'Awaiting first tick'}</div>
          </div>
          <div>
            <div className="text-gray-400">Dhan /orders API</div>
            <div className="text-lg font-bold text-green-400">
              {orderCalled ? 'CALLED (BLOCK)' : 'INTENTIONALLY NOT CALLED'}
            </div>
            <div className="text-xs text-gray-500 mt-1">Correct for paper — broker order endpoints remain disabled</div>
          </div>
        </div>
      </div>

      <DataSourceWarning dataSource={String(dataSource)} brokerConnected={brokerConnected} mode={mode} />

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-2">Open Paper Positions ({positions.length})</h3>
        <div className="text-xs text-gray-500 mb-4">
          Dhan-aligned fields: symbol, CE/PE, strike, expiry, buy average, LTP, quantity, unrealized PnL, SL and target.
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
                        FIRESTORE_PAPER_LEDGER<br/>
                        {pos.market_data_source || pos.data_source || dataSource}<br/>
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
              The durable ledger is available. New paper fills are created only by the bounded Cloud Run paper job when real Dhan selection gates pass.
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">PnL Summary (Paper Ledger)</h3>
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
            <div>Paper lifecycle → <span className="text-green-400">FIRESTORE_PAPER_LEDGER</span></div>
            <div>Market quotes → <span className="text-gray-300">DHAN OPTION CHAIN READ ONLY</span></div>
            <div>Execution mode → <span className="text-green-400">ANALYZER / PAPER</span></div>
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
              <div className="text-sm text-gray-500">No durable entries yet today.</div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-auto">
                {todayEntries.slice(0, 20).map((e: any, i: number) => (
                  <div key={e.event_id || i} className="bg-gray-900 p-3 rounded text-xs font-mono">
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
              <div className="text-sm text-gray-500">No durable exits yet today.</div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-auto">
                {todayExits.slice(0, 20).map((e: any, i: number) => (
                  <div key={e.event_id || i} className="bg-gray-900 p-3 rounded text-xs font-mono">
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
