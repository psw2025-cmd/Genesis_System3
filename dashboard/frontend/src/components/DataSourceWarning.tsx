import React from 'react'

interface DataSourceWarningProps {
  dataSource: string
  brokerConnected: boolean
  mode: string
  lastDataTime?: string | null
  dataAgeSeconds?: number | null
}

function formatLastUpdated(iso: string | undefined | null): string {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'medium' })
  } catch {
    return iso
  }
}

export default function DataSourceWarning({
  dataSource,
  brokerConnected,
  mode,
  lastDataTime,
  dataAgeSeconds
}: DataSourceWarningProps) {
  const ds = (dataSource || '').toLowerCase()
  const isLive = ds === 'live'
  const isCached = ds === 'cached'
  const isNotReady = ds === 'not_ready'
  const isPaper = mode === 'PAPER' || mode === 'paper'

  // Live data badge (market open, streaming)
  if (isLive && isPaper) {
    return (
      <div className="bg-green-900/20 border border-green-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">🟢</div>
          <div className="flex-1">
            <div className="font-bold text-green-400 mb-1">
              LIVE DATA – PAPER TRADING MODE
            </div>
            <div className="text-sm text-green-300 mb-2">
              Real-time market data. All trades are simulated. No real orders.
              {dataAgeSeconds != null && dataAgeSeconds >= 0 && (
                <span className="block mt-1 text-green-400/90">
                  Last updated: {dataAgeSeconds < 60 ? `${Math.round(dataAgeSeconds)}s ago` : formatLastUpdated(lastDataTime)}
                </span>
              )}
            </div>
            <div className="text-xs text-green-400/80">
              Data: <strong>LIVE</strong> | Broker: <strong>{brokerConnected ? 'Connected' : 'Disconnected'}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Cached data (market closed, showing last known)
  if (isCached) {
    return (
      <div className="bg-amber-900/20 border border-amber-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">📦</div>
          <div className="flex-1">
            <div className="font-bold text-amber-400 mb-1">
              CACHED DATA (Market Closed)
            </div>
            <div className="text-sm text-amber-300 mb-2">
              Showing last known data. Live streaming resumes when market opens (9:15–15:30 IST).
              {lastDataTime && (
                <span className="block mt-1 text-amber-400/90">
                  Last updated: {formatLastUpdated(lastDataTime)}
                  {dataAgeSeconds != null && dataAgeSeconds >= 0 && (
                    <span> ({Math.round(dataAgeSeconds / 60)} min ago)</span>
                  )}
                </span>
              )}
            </div>
            <div className="text-xs text-amber-400/80">
              Data: <strong>CACHED</strong> | live_allowed: <strong>false</strong> (market closed)
            </div>
          </div>
        </div>
      </div>
    )
  }

  // PAPER mode with not_ready or other
  if (isPaper) {
    return (
      <div className="bg-blue-900/20 border border-blue-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">📊</div>
          <div className="flex-1">
            <div className="font-bold text-blue-400 mb-1">
              PAPER TRADING MODE (NO REAL ORDERS)
            </div>
            <div className="text-sm text-blue-300 mb-2">
              {isNotReady
                ? 'No data yet. Start the trading system or wait for market open to fetch data.'
                : 'System is in PAPER mode. All trades are simulated.'}
            </div>
            <div className="text-xs text-blue-400/80">
              Data: <strong>{dataSource || 'NOT_READY'}</strong> | Broker: <strong>{brokerConnected ? 'Connected' : 'Disconnected'}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Fallback
  if (!brokerConnected || isNotReady) {
    return (
      <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">⚠️</div>
          <div className="flex-1">
            <div className="font-bold text-yellow-400 mb-1">
              {!brokerConnected ? 'BROKER DISCONNECTED' : 'DATA NOT READY'}
            </div>
            <div className="text-sm text-yellow-300 mb-2">
              {!brokerConnected
                ? 'Broker is disconnected. Trading actions are disabled.'
                : 'No data available. Start the trading system or wait for first fetch.'}
            </div>
            <div className="text-xs text-yellow-400/80">
              Data: <strong>{dataSource}</strong> | Broker: <strong>{brokerConnected ? 'Connected' : 'Disconnected'}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return null
}
