import React from 'react'

interface DataSourceWarningProps {
  dataSource: string
  brokerConnected: boolean
  mode: string
}

function isUsableMarketSource(dataSource: string, brokerConnected: boolean) {
  const s = String(dataSource || '').toUpperCase()
  if (brokerConnected) return true
  return (
    s === 'REAL'
    || s.includes('DHAN')
    || s.includes('BROKER_LIVE')
    || s.includes('MARK_TO_MARKET')
    || s.includes('OPTION_CHAIN')
    || s.includes('LIVE')
  )
}

export default function DataSourceWarning({ dataSource, brokerConnected, mode }: DataSourceWarningProps) {
  const modeUp = String(mode || '').toUpperCase()
  const isPaper = modeUp.includes('PAPER') || modeUp.includes('ANALYZER')
  const marketOk = isUsableMarketSource(dataSource, brokerConnected)

  if (isPaper) {
    return (
      <div className="bg-blue-900/20 border border-blue-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <div className="font-bold text-blue-400 mb-1">
              PAPER TRADING MODE (NO REAL ORDERS)
            </div>
            <div className="text-sm text-blue-300 mb-2">
              Fills are simulated locally. Dhan /orders APIs are intentionally not called.
              {marketOk
                ? ' Mark-to-market uses live Dhan option-chain LTP.'
                : ' Waiting for Dhan market data — paper MTM may be stale until chain reconnects.'}
            </div>
            <div className="text-xs text-blue-400/80">
              Mode: <strong className="text-blue-300">PAPER</strong>
              {' | '}Data Source: <strong>{marketOk ? String(dataSource || 'DHAN_LIVE') : 'WAITING_DHAN'}</strong>
              {' | '}Broker: <strong>{brokerConnected ? 'Connected' : marketOk ? 'Chain usable' : 'Disconnected'}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!marketOk) {
    return (
      <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg mb-4">
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <div className="font-bold text-yellow-400 mb-1">
              {!brokerConnected ? 'BROKER DISCONNECTED' : 'MARKET DATA NOT READY'}
            </div>
            <div className="text-sm text-yellow-300 mb-2">
              Real market data is unavailable. Trading actions stay disabled.
            </div>
            <div className="text-xs text-yellow-400/80">
              Data Source: <strong>{dataSource}</strong>
              {' | '}Broker: <strong>{brokerConnected ? 'Connected' : 'Disconnected'}</strong>
              {' | '}Mode: <strong>{mode}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return null
}
