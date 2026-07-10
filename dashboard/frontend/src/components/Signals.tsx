import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import EmptyState from './EmptyState'
import ErrorBanner from './ErrorBanner'
import { AuthUnlock } from './AuthUnlock'

type SignalView = {
  action: string
  underlying: string
  strategy: string
  confidence: number
  direction: string
  reason: string
  source?: string
  option_type?: string
  strike?: number | string
  expiry_date?: string
  trading_symbol?: string
  ltp?: number
  gain_pct?: number
  entry_mid?: number
  stop_loss?: number
  target?: number
  raw?: any
}

function firstCandidateFromScanner(scanner: any): any | null {
  const paths = [
    scanner?.market_wide?.top_ce,
    scanner?.market_wide?.top_pe,
  ]
  const bySegment = scanner?.by_segment || {}
  for (const seg of Object.values(bySegment) as any[]) {
    paths.push(seg?.top_ce, seg?.top_pe)
    if (Array.isArray(seg?.top_ce_list)) paths.push(...seg.top_ce_list)
    if (Array.isArray(seg?.top_pe_list)) paths.push(...seg.top_pe_list)
  }
  const rows = paths.filter(Boolean)
  if (!rows.length) return null
  rows.sort((a: any, b: any) => Number(b?.gain_pct || 0) - Number(a?.gain_pct || 0))
  return rows[0]
}

function firstCandidateFromGain(gain: any): any | null {
  const rows: any[] = []
  const walk = (x: any, depth = 0) => {
    if (!x || depth > 8) return
    if (Array.isArray(x)) {
      for (const item of x) walk(item, depth + 1)
      return
    }
    if (typeof x !== 'object') return
    const hasName = x.underlying || x.symbol || x.trading_symbol || x.ticker
    const hasSide = x.option_side || x.option_type || x.signal_type || x.side || x.direction
    const hasScore = x.score !== undefined || x.confidence !== undefined || x.display_score !== undefined || x.gain_pct !== undefined
    if (hasName && (hasSide || hasScore)) rows.push(x)
    for (const key of ['latest', 'data', 'rankings', 'predictions', 'candidates', 'signals', 'top5', 'top', 'entries']) {
      if (x[key]) walk(x[key], depth + 1)
    }
  }
  walk(gain)
  if (!rows.length) return null
  rows.sort((a, b) => Number(b?.confidence ?? b?.score ?? b?.display_score ?? b?.gain_pct ?? 0) - Number(a?.confidence ?? a?.score ?? a?.display_score ?? a?.gain_pct ?? 0))
  return rows[0]
}

function asSignalFromCandidate(candidate: any, source: string): SignalView {
  const opt = String(candidate.option_type || candidate.option_side || candidate.signal_type || candidate.side || '').toUpperCase()
  const isPe = opt.includes('PE') || opt.includes('PUT')
  const isCe = opt.includes('CE') || opt.includes('CALL')
  const gain = Number(candidate.gain_pct ?? candidate.change_percent ?? 0)
  const confidenceRaw = Number(candidate.confidence ?? candidate.score ?? candidate.display_score ?? Math.max(0, Math.min(100, Math.abs(gain))))
  const confidence = confidenceRaw > 1 ? confidenceRaw / 100 : confidenceRaw
  const ltp = Number(candidate.ltp ?? candidate.last_price ?? 0)
  return {
    action: 'TRADE_CANDIDATE_ONLY',
    underlying: candidate.underlying || candidate.symbol || candidate.ticker || 'N/A',
    strategy: `${source}: ${isPe ? 'PE' : isCe ? 'CE' : opt || 'OPTION'} candidate evidence`,
    confidence: Number.isFinite(confidence) ? confidence : 0,
    direction: isPe ? 'PE' : isCe ? 'CE' : opt || 'NONE',
    reason: 'Candidate evidence exists, but broker order remains blocked until risk/paper lifecycle gates pass.',
    source,
    option_type: isPe ? 'PE' : isCe ? 'CE' : opt,
    strike: candidate.strike,
    expiry_date: candidate.expiry_date || candidate.expiry,
    trading_symbol: candidate.trading_symbol || candidate.symbol,
    ltp: Number.isFinite(ltp) ? ltp : undefined,
    gain_pct: Number.isFinite(gain) ? gain : undefined,
    entry_mid: Number.isFinite(ltp) && ltp > 0 ? ltp : undefined,
    stop_loss: Number.isFinite(ltp) && ltp > 0 ? Number((ltp * 0.8).toFixed(2)) : undefined,
    target: Number.isFinite(ltp) && ltp > 0 ? Number((ltp * 1.3).toFixed(2)) : undefined,
    raw: candidate,
  }
}

export default function Signals() {
  const [signal, setSignal] = useState<SignalView | null>(null)
  const [qc, setQc] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [authRequired, setAuthRequired] = useState(false)
  const [error, setError] = useState<{endpoint: string, status?: number, message: string} | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      const [stateRes, scannerRes, gainRes] = await Promise.allSettled([
        axios.get(`${API_BASE}/api/state`),
        axios.get(`${API_BASE}/api/scanner/top_contract_gainers?top_n=5`),
        axios.get(`${API_BASE}/api/gain_rank`),
      ])

      if (stateRes.status === 'rejected') {
        const status = (stateRes.reason as any)?.response?.status || null
        if (status === 401) {
          setAuthRequired(true)
          setError(null)
          setSignal(null)
          setQc({ status: 'LOCKED', total_contracts: 0, underlyings: 0, failures: ['Dashboard API auth required'] })
          return
        }
        throw stateRes.reason
      }

      const state = stateRes.value.data
      const scanner = scannerRes.status === 'fulfilled' ? scannerRes.value.data : null
      const gain = gainRes.status === 'fulfilled' ? gainRes.value.data : null
      const scannerCandidate = firstCandidateFromScanner(scanner)
      const gainCandidate = firstCandidateFromGain(gain)
      const candidate = scannerCandidate || gainCandidate

      const stateSignals = state.signals || {}
      let signalData: SignalView
      if (candidate) {
        signalData = asSignalFromCandidate(candidate, scannerCandidate ? 'scanner_top_contract_gainers' : 'gain_rank')
      } else {
        signalData = {
          action: stateSignals.status === 'BUY' || stateSignals.status === 'SELL' ? 'TRADE' : 'NO_TRADE',
          underlying: stateSignals.underlying || 'N/A',
          strategy: stateSignals.reason || 'NONE',
          confidence: (stateSignals.confidence || 0) / 100,
          direction: stateSignals.status === 'BUY' ? 'LONG' : stateSignals.status === 'SELL' ? 'SHORT' : 'NONE',
          reason: stateSignals.reason || state.market?.reason || 'No scanner/ranker candidate generated',
          source: 'runtime_state',
          raw: stateSignals,
        }
      }

      const scannerImplemented = Number(scanner?.segments_implemented || 0)
      const scannerTotal = Number(scanner?.segments_total || 0)
      const qcFailures = [
        ...(state.qc?.qc_failures || state.qc?.failures || []),
        ...(scannerRes.status === 'rejected' ? [`scanner endpoint failed: ${(scannerRes.reason as any)?.message || 'unknown'}`] : []),
        ...(gainRes.status === 'rejected' ? [`gain_rank endpoint failed: ${(gainRes.reason as any)?.message || 'unknown'}`] : []),
      ]

      const qcData = {
        status: candidate ? 'PASS' : (state.qc?.status || 'PASS'),
        total_contracts: state.qc?.contracts_total || 0,
        underlyings: state.qc?.underlyings || scannerImplemented || 0,
        scanner_segments: `${scannerImplemented}/${scannerTotal || '-'}`,
        failures: qcFailures,
        no_trade_reasons: state.qc?.no_trade_reasons || {},
        qc_failures: qcFailures,
      }

      setSignal(signalData)
      setQc(qcData)
      setAuthRequired(false)
      setError(null)
    } catch (error: any) {
      const status = error.response?.status || null
      if (status === 401) {
        setAuthRequired(true)
        setError(null)
        setSignal(null)
        setQc({ status: 'LOCKED', total_contracts: 0, underlyings: 0, failures: ['Dashboard API auth required'] })
      } else {
        setAuthRequired(false)
        setError({ endpoint: `${API_BASE}/api/state`, status: status || undefined, message: error.message || 'Failed to fetch signal data' })
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (isLoading && !signal && !authRequired) {
    return <div className="p-6"><div className="text-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div><div className="text-xl font-bold">Loading signals...</div></div></div>
  }

  if (authRequired) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Signals & Recommendations</h2>
        <div className="card p-4 border border-amber/30 bg-amber/5">
          <div className="text-xs text-text-muted uppercase tracking-wider">Signal Data Locked</div>
          <div className="text-sm text-text-primary font-semibold">Dashboard API auth is required before signals can be read.</div>
          <div className="mt-2 text-xs text-text-muted">This is a read-only lock. Live trading remains disabled.</div>
        </div>
        <AuthUnlock />
        <EmptyState title="Signals locked" reason="Enter the Dashboard API key to unlock read-only signal, broker, paper, scanner and gate data." icon="LOCK" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Signals & Recommendations</h2>
        <ErrorBanner endpoint={error.endpoint} status={error.status} message={error.message} onRetry={fetchData} />
        <EmptyState title="Signal data unavailable" reason="Backend did not return signal/state data. Check API health and deployment." icon="INFO" />
      </div>
    )
  }

  if (!signal) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Signals & Recommendations</h2>
        <EmptyState title="No signals available" reason="No trading signals generated yet. Signals will appear when market conditions are met." icon="INFO" />
      </div>
    )
  }

  const isTrade = signal.action === 'TRADE'
  const isCandidate = signal.action === 'TRADE_CANDIDATE_ONLY'
  const isManaging = signal.action === 'MANAGING_POSITION' || signal.reason?.includes('Managing')

  const blockingReasons: string[] = []
  if (qc?.status === 'FAIL') blockingReasons.push('QC Fail')
  if (!signal.underlying || signal.underlying === 'N/A') blockingReasons.push('No Underlying')
  if ((signal.confidence || 0) < 0.5 && !isCandidate) blockingReasons.push('Low Confidence')
  if (signal.reason?.toLowerCase?.().includes('market closed')) blockingReasons.push('Market Closed')
  if (isCandidate) blockingReasons.push('Candidate only: paper/risk/live gates still decide whether trade is allowed')

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Signals & Recommendations</h2>

      <div className={`p-6 rounded-lg ${isTrade ? 'bg-green-900' : isCandidate ? 'bg-indigo-900' : isManaging ? 'bg-blue-900' : 'bg-gray-800'}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-bold">{isTrade ? 'TRADE SIGNAL' : isCandidate ? 'REAL CANDIDATE EVIDENCE' : isManaging ? 'MANAGING POSITIONS' : 'NO TRADE'}</h3>
          <div className={`px-4 py-2 rounded ${isTrade ? 'bg-green-600' : isCandidate ? 'bg-indigo-600' : isManaging ? 'bg-blue-600' : 'bg-gray-600'}`}>{signal.action}</div>
        </div>

        {isCandidate && (
          <div className="mb-4 p-3 bg-indigo-800 rounded">
            <div className="text-sm font-bold">Read-only scanner/ranker evidence found.</div>
            <div className="text-xs mt-1">This is not a broker order. Live trading remains disabled until paper/risk gates prove readiness.</div>
          </div>
        )}

        {isManaging && <div className="mb-4 p-3 bg-blue-800 rounded"><div className="text-sm">Currently managing open positions. No new trades until positions are closed.</div></div>}

        {blockingReasons.length > 0 && !isTrade && !isManaging && (
          <div className="mb-4 p-3 bg-yellow-900 rounded">
            <div className="text-sm font-bold mb-2">What Blocked Trading?</div>
            <ul className="list-disc list-inside text-sm">{blockingReasons.map((reason, idx) => <li key={idx}>{reason}</li>)}</ul>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><div className="text-sm text-gray-400">Underlying</div><div className="text-xl font-bold">{signal.underlying || 'N/A'}</div></div>
          <div><div className="text-sm text-gray-400">Strategy</div><div className="text-xl font-bold">{signal.strategy || 'NONE'}</div></div>
          <div><div className="text-sm text-gray-400">Confidence</div><div className="text-xl font-bold">{signal.confidence ? (signal.confidence * 100).toFixed(1) + '%' : 'N/A'}</div></div>
        </div>

        {(isTrade || isCandidate) && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div><div className="text-sm text-gray-400">Side</div><div className="text-lg">{signal.option_type || signal.direction || 'N/A'}</div></div>
            <div><div className="text-sm text-gray-400">Strike</div><div className="text-lg">{signal.strike || 'N/A'}</div></div>
            <div><div className="text-sm text-gray-400">Expiry</div><div className="text-lg">{signal.expiry_date || 'N/A'}</div></div>
            <div><div className="text-sm text-gray-400">Gain %</div><div className="text-lg">{signal.gain_pct !== undefined ? signal.gain_pct.toFixed(2) + '%' : 'N/A'}</div></div>
          </div>
        )}

        {(isTrade || isCandidate) && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><div className="text-sm text-gray-400">Entry Mid</div><div className="text-lg">Rs {signal.entry_mid?.toFixed(2) || 'N/A'}</div></div>
            <div><div className="text-sm text-gray-400">Stop Loss</div><div className="text-lg">Rs {signal.stop_loss?.toFixed(2) || 'N/A'}</div></div>
            <div><div className="text-sm text-gray-400">Target</div><div className="text-lg">Rs {signal.target?.toFixed(2) || 'N/A'}</div></div>
          </div>
        )}
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Explainability</h3>
        <div className="space-y-2">
          <div><div className="text-sm text-gray-400">Reason</div><div className="text-lg">{signal.reason || 'N/A'}</div></div>
          <div><div className="text-sm text-gray-400">Source</div><div className="text-lg">{signal.source || 'N/A'}</div></div>
          {signal.trading_symbol && <div><div className="text-sm text-gray-400">Contract</div><div className="text-lg">{signal.trading_symbol}</div></div>}
        </div>
      </div>

      {!isTrade && qc && (
        <div className="bg-red-900 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">What Blocked Trading?</h3>
          <div className="space-y-2">
            <div><div className="text-sm text-gray-300">Scanner Segments</div><div>{qc.scanner_segments || 'N/A'}</div></div>
            {qc.no_trade_reasons && Object.keys(qc.no_trade_reasons).length > 0 && (
              <div><div className="text-sm text-gray-300">NO_TRADE Reasons</div><ul className="list-disc list-inside">{Object.entries(qc.no_trade_reasons).map(([reason, count]: [string, any]) => <li key={reason}>{reason}: {count} times</li>)}</ul></div>
            )}
            {qc.qc_failures && qc.qc_failures.length > 0 && (
              <div><div className="text-sm text-gray-300">QC Failures</div><ul className="list-disc list-inside">{qc.qc_failures.slice(0, 5).map((failure: string, idx: number) => <li key={idx}>{failure}</li>)}</ul></div>
            )}
          </div>
        </div>
      )}

      <div className="bg-gray-800 p-4 rounded-lg">
        <button
          onClick={() => {
            const blob = new Blob([JSON.stringify(signal, null, 2)], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `signal_${new Date().toISOString()}.json`
            a.click()
          }}
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
        >
          Download Signal Snapshot (JSON)
        </button>
      </div>
    </div>
  )
}
