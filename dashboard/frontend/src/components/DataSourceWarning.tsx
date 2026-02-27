import React from 'react'

interface DataSourceWarningProps {
  dataSource: string
  brokerConnected: boolean
  mode: string
}

export default function DataSourceWarning({ dataSource, brokerConnected, mode }: DataSourceWarningProps) {
  const isReal = dataSource === 'REAL' || dataSource === 'real'
  const isPaper = mode === 'PAPER' || mode === 'paper'
  
  // Always show PAPER mode indicator (even with real data)
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
              System is in PAPER mode. All trades are simulated. No real money orders will be placed.
              {isReal && brokerConnected 
                ? ' Using real market data for accurate simulation.'
                : ' Broker not ready - real data unavailable.'}
            </div>
            <div className="text-xs text-blue-400/80">
              Mode: <strong className="text-blue-300">PAPER</strong> | 
              Data Source: <strong>{isReal ? 'LIVE' : 'NOT_READY'}</strong> | 
              Broker: <strong>{brokerConnected ? 'Connected' : 'Disconnected'}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }
  
  // Fallback for other modes
  if (!isReal || !brokerConnected) {
    return (
      <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">⚠️</div>
          <div className="flex-1">
            <div className="font-bold text-yellow-400 mb-1">
              {!isReal ? 'BROKER NOT READY' : 'BROKER DISCONNECTED'}
            </div>
            <div className="text-sm text-yellow-300 mb-2">
              {!isReal 
                ? 'Broker is not ready. Real market data is unavailable. Trading actions are disabled.'
                : 'Broker is disconnected. Positions shown are unverified. Trading actions are disabled.'}
            </div>
            <div className="text-xs text-yellow-400/80">
              Data Source: <strong>{dataSource}</strong> | 
              Broker: <strong>{brokerConnected ? 'Connected' : 'Disconnected'}</strong> | 
              Mode: <strong>{mode}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }
  
  return null
}
