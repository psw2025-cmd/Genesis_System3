import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import EmptyState from './EmptyState'
import ErrorBanner from './ErrorBanner'

export default function Signals() {
  const [signal, setSignal] = useState<any>(null)
  const [qc, setQc] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<{endpoint: string, status?: number, message: string} | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Use SSOT for consistency
        const stateRes = await axios.get(`${API_BASE}/api/state`)
        const state = stateRes.data
        
        // Convert SSOT signals to signal format
        const signals = state.signals || {}
        const signalData = {
          action: signals.status === 'BUY' || signals.status === 'SELL' ? 'TRADE' : 'NO_TRADE',
          underlying: signals.underlying || 'N/A',
          strategy: signals.reason || 'NONE',
          confidence: (signals.confidence || 0) / 100, // Convert from 0-100 to 0-1
          direction: signals.status === 'BUY' ? 'LONG' : signals.status === 'SELL' ? 'SHORT' : 'NONE',
          reason: signals.reason || 'No signal generated'
        }
        
        // Convert SSOT QC to QC format
        const qcData = {
          status: state.qc?.status || 'PASS',
          total_contracts: state.qc?.contracts_total || 0,
          underlyings: state.qc?.underlyings || 0,
          failures: state.qc?.failures || []
        }
        
        setSignal(signalData)
        setQc(qcData)
        setError(null)
      } catch (error: any) {
        console.error('Error fetching signals:', error)
        const errorMsg = error.message || 'Unknown error'
        const status = error.response?.status || null
        setError({
          endpoint: `${API_BASE}/api/state`,
          status: status || undefined,
          message: errorMsg
        })
        // Fallback to old endpoints
        try {
          const [signalRes, qcRes] = await Promise.all([
            axios.get(`${API_BASE}/api/signal/top`),
            axios.get(`${API_BASE}/api/qc`)
          ])
          setSignal(signalRes.data)
          setQc(qcRes.data)
          setError(null)
        } catch (fallbackError: any) {
          console.error('Fallback also failed:', fallbackError)
          const fallbackStatus = fallbackError.response?.status || null
          setError({
            endpoint: `${API_BASE}/api/signal/top`,
            status: fallbackStatus || undefined,
            message: fallbackError.message || 'Failed to fetch signal data'
          })
        }
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
    // Optimized polling: 3000ms (3 seconds) instead of 2000ms
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [])

  if (isLoading && !signal) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-xl font-bold">Loading signals...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Signals & Recommendations</h2>
        <ErrorBanner
          endpoint={error.endpoint}
          status={error.status}
          message={error.message}
          onRetry={() => {
            setIsLoading(true)
            setError(null)
            // Trigger re-fetch
            window.location.reload()
          }}
        />
        <EmptyState
          title="Signal data unavailable"
          reason="Unable to load trading signals. Please check backend connection."
          icon="📡"
        />
      </div>
    )
  }

  if (!signal) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Signals & Recommendations</h2>
        <EmptyState
          title="No signals available"
          reason="No trading signals generated yet. Signals will appear when market conditions are met."
          icon="📊"
        />
      </div>
    )
  }

  const isTrade = signal.action === 'TRADE'
  const isManaging = signal.action === 'MANAGING_POSITION' || signal.reason?.includes('Managing')
  
  // Get blocking reasons from SSOT (if available)
  const blockingReasons: string[] = []
  if (qc?.status === 'FAIL') blockingReasons.push('QC Fail')
  if (!signal.underlying || signal.underlying === 'N/A') blockingReasons.push('No Underlying')
  if ((signal.confidence || 0) < 0.5) blockingReasons.push('Low Confidence')
  if (signal.reason?.includes('market closed')) blockingReasons.push('Market Closed')

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Signals & Recommendations</h2>

      {/* Top Signal Card */}
      <div className={`p-6 rounded-lg ${isTrade ? 'bg-green-900' : isManaging ? 'bg-blue-900' : 'bg-gray-800'}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-bold">
            {isTrade ? 'TRADE SIGNAL' : isManaging ? 'MANAGING POSITIONS' : 'NO TRADE'}
          </h3>
          <div className={`px-4 py-2 rounded ${isTrade ? 'bg-green-600' : isManaging ? 'bg-blue-600' : 'bg-gray-600'}`}>
            {signal.action}
          </div>
        </div>
        
        {isManaging && (
          <div className="mb-4 p-3 bg-blue-800 rounded">
            <div className="text-sm">Currently managing open positions. No new trades until positions are closed.</div>
          </div>
        )}
        
        {blockingReasons.length > 0 && !isTrade && !isManaging && (
          <div className="mb-4 p-3 bg-yellow-900 rounded">
            <div className="text-sm font-bold mb-2">What Blocked Trading?</div>
            <ul className="list-disc list-inside text-sm">
              {blockingReasons.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-400">Underlying</div>
            <div className="text-xl font-bold">{signal.underlying || signal.symbol || 'N/A'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Strategy</div>
            <div className="text-xl font-bold">{signal.strategy || signal.candidate_strategy || 'NONE'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Confidence</div>
            <div className="text-xl font-bold">
              {signal.confidence ? (signal.confidence * 100).toFixed(1) + '%' : 'N/A'}
            </div>
          </div>
        </div>

        {isTrade && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-400">Entry Mid</div>
              <div className="text-lg">₹{signal.entry_mid?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Stop Loss</div>
              <div className="text-lg">₹{signal.stop_loss?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Target</div>
              <div className="text-lg">₹{signal.target?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>
        )}
      </div>

      {/* Explainability Panel */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Explainability</h3>
        <div className="space-y-2">
          <div>
            <div className="text-sm text-gray-400">Reason</div>
            <div className="text-lg">{signal.reason || 'N/A'}</div>
          </div>
          {signal.reasons && signal.reasons.length > 0 && (
            <div>
              <div className="text-sm text-gray-400">Reasons List</div>
              <ul className="list-disc list-inside">
                {signal.reasons.map((r: string, idx: number) => (
                  <li key={idx}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* What Blocked Trading */}
      {!isTrade && qc && (
        <div className="bg-red-900 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">What Blocked Trading?</h3>
          <div className="space-y-2">
            {qc.no_trade_reasons && Object.keys(qc.no_trade_reasons).length > 0 && (
              <div>
                <div className="text-sm text-gray-300">NO_TRADE Reasons</div>
                <ul className="list-disc list-inside">
                  {Object.entries(qc.no_trade_reasons).map(([reason, count]: [string, any]) => (
                    <li key={reason}>{reason}: {count} times</li>
                  ))}
                </ul>
              </div>
            )}
            {qc.qc_failures && qc.qc_failures.length > 0 && (
              <div>
                <div className="text-sm text-gray-300">QC Failures</div>
                <ul className="list-disc list-inside">
                  {qc.qc_failures.slice(0, 5).map((failure: string, idx: number) => (
                    <li key={idx}>{failure}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Export */}
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
