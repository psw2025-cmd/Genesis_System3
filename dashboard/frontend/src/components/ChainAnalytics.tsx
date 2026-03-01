import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

const UNDERLYINGS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

export default function ChainAnalytics() {
  const [selectedUnderlying, setSelectedUnderlying] = useState('NIFTY')
  const [chainData, setChainData] = useState<any>(null)
  const [filters, setFilters] = useState({
    strikeRange: { min: 0, max: 999999 },
    nearATM: false,
    liquidityThreshold: 0,
    showInvalid: false
  })

  useEffect(() => {
    const fetchChain = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/chain/${selectedUnderlying}`)
        setChainData(res.data)
      } catch (error) {
        console.error('Error fetching chain:', error)
        // Set error state so UI doesn't stay in loading
        setChainData({
          underlying: selectedUnderlying,
          contracts: [],
          spot: 0,
          pcr: 1.0,
          total_contracts: 0,
          message: 'Error fetching chain data',
          status: 'ERROR'
        })
      }
    }
    fetchChain()
    // Optimized polling: 5000ms (5 seconds) - already optimal
    const interval = setInterval(fetchChain, 5000)
    return () => clearInterval(interval)
  }, [selectedUnderlying])

  if (!chainData) {
    return <div className="p-6">Loading chain data...</div>
  }

  // Handle broker not ready - show NOT_READY status
  const isNotReady = chainData.data_source === 'not_ready' || chainData.data_source === 'synthetic' || chainData.status === 'NOT_READY'

  if (chainData.message && chainData.total_contracts === 0) {
    return (
      <div className="p-6 space-y-4">
        <h2 className="text-3xl font-bold">Option Chain Analytics</h2>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-xl font-bold mb-2">No Data Available</h3>
          <p className="text-gray-300">{chainData.message}</p>
          <p className="text-sm text-gray-400 mt-2">Selected Underlying: <strong>{selectedUnderlying}</strong></p>
        </div>
        <div className="flex gap-2">
          {UNDERLYINGS.map(u => (
            <button
              key={u}
              onClick={() => setSelectedUnderlying(u)}
              className={`px-4 py-2 rounded ${selectedUnderlying === u ? 'bg-blue-600' : 'bg-gray-700'}`}
            >
              {u}
            </button>
          ))}
        </div>
      </div>
    )
  }

  const contracts = chainData.contracts || []
  const spot = chainData.spot || 0

  // Filter contracts
  let filteredContracts = contracts
  if (filters.nearATM && spot > 0) {
    const atmBand = spot * 0.05
    filteredContracts = filteredContracts.filter((c: any) => 
      Math.abs((c.strike || 0) - spot) <= atmBand
    )
  }
  if (filters.strikeRange) {
    filteredContracts = filteredContracts.filter((c: any) => 
      (c.strike || 0) >= filters.strikeRange.min && 
      (c.strike || 0) <= filters.strikeRange.max
    )
  }
  if (filters.liquidityThreshold > 0) {
    filteredContracts = filteredContracts.filter((c: any) => 
      (c.liquidity_score || 0) >= filters.liquidityThreshold
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Option Chain Analytics</h2>
        {isNotReady && (
          <div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-sm">
            ⚠️ BROKER NOT READY
          </div>
        )}
        {!isNotReady && (chainData.data_source === 'real' || chainData.data_source === 'live') && (
          <div className="bg-green-500 text-white px-4 py-2 rounded-lg font-bold text-sm">
            ✅ LIVE MARKET DATA
          </div>
        )}
      </div>

      {/* Underlying Selector */}
      <div className="flex gap-2">
        {UNDERLYINGS.map(u => (
          <button
            key={u}
            onClick={() => setSelectedUnderlying(u)}
            className={`px-4 py-2 rounded ${selectedUnderlying === u ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            {u}
          </button>
        ))}
      </div>

      {/* Market Mode Banner - Angel parity: LIVE / MARKET CLOSED / PRE-OPEN */}
      {(chainData.market_mode === 'closed' || chainData.status === 'MARKET_CLOSED') && (
        <div className="bg-amber-900/40 border border-amber-600 px-4 py-3 rounded-lg font-bold">
          🔒 MARKET CLOSED — Showing last session / synthetic data (Off-Market mode)
        </div>
      )}
      {chainData.market_mode === 'preopen' && (
        <div className="bg-blue-900/40 border border-blue-600 px-4 py-3 rounded-lg font-bold">
          ⏳ PRE-MARKET (9:00–9:15 AM) — Market opens at 9:15 AM IST
        </div>
      )}
      {chainData.market_mode === 'live' && (chainData.data_source === 'real' || chainData.data_source === 'live') && (
        <div className="bg-green-900/40 border border-green-600 px-4 py-3 rounded-lg font-bold">
          ✅ LIVE — Real-time market data
        </div>
      )}

      {/* Metrics - Angel parity: Spot, PCR, Max Pain, Total Contracts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Spot Price</div>
          <div className="text-2xl font-bold">₹{spot.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Put-Call Ratio</div>
          <div className="text-2xl font-bold">{chainData.pcr?.toFixed(2) || 'N/A'}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Max Pain</div>
          <div className="text-2xl font-bold">{chainData.max_pain != null ? `₹${chainData.max_pain.toFixed(0)}` : 'N/A'}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Total Contracts</div>
          <div className="text-2xl font-bold">{chainData.total_contracts || 0}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Filtered</div>
          <div className="text-2xl font-bold">{filteredContracts.length}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-lg font-bold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm mb-2">Strike Range</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={filters.strikeRange.min}
                onChange={(e) => setFilters({...filters, strikeRange: {...filters.strikeRange, min: Number(e.target.value)}})}
                className="w-24 px-2 py-1 bg-gray-700 rounded"
              />
              <span>-</span>
              <input
                type="number"
                value={filters.strikeRange.max}
                onChange={(e) => setFilters({...filters, strikeRange: {...filters.strikeRange, max: Number(e.target.value)}})}
                className="w-24 px-2 py-1 bg-gray-700 rounded"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm mb-2">
              <input
                type="checkbox"
                checked={filters.nearATM}
                onChange={(e) => setFilters({...filters, nearATM: e.target.checked})}
                className="mr-2"
              />
              Near ATM (±5%)
            </label>
          </div>
          <div>
            <label className="block text-sm mb-2">Liquidity Threshold</label>
            <input
              type="number"
              value={filters.liquidityThreshold}
              onChange={(e) => setFilters({...filters, liquidityThreshold: Number(e.target.value)})}
              className="w-full px-2 py-1 bg-gray-700 rounded"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">
              <input
                type="checkbox"
                checked={filters.showInvalid}
                onChange={(e) => setFilters({...filters, showInvalid: e.target.checked})}
                className="mr-2"
              />
              Show Invalid (QC Failed)
            </label>
          </div>
        </div>
      </div>

      {/* Chain Table */}
      <div className="bg-gray-800 p-4 rounded-lg overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left p-2">Strike</th>
              <th className="text-left p-2">Type</th>
              <th className="text-right p-2">LTP</th>
              <th className="text-right p-2">Bid</th>
              <th className="text-right p-2">Ask</th>
              <th className="text-right p-2">OI</th>
              <th className="text-right p-2">OI Chg%</th>
              <th className="text-right p-2">Volume</th>
              <th className="text-right p-2">IV</th>
              <th className="text-right p-2">Delta</th>
              <th className="text-right p-2">Gamma</th>
              <th className="text-right p-2">Vega</th>
              <th className="text-right p-2">Theta</th>
              <th className="text-right p-2">Liquidity</th>
            </tr>
          </thead>
          <tbody>
            {filteredContracts.slice(0, 100).map((contract: any, idx: number) => (
              <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                <td className="p-2">{contract.strike || 'N/A'}</td>
                <td className="p-2">{contract.option_type || 'N/A'}</td>
                <td className="text-right p-2">₹{contract.ltp?.toFixed(2) || 'N/A'}</td>
                <td className="text-right p-2">₹{contract.bid?.toFixed(2) ?? 'N/A'}</td>
                <td className="text-right p-2">₹{contract.ask?.toFixed(2) ?? 'N/A'}</td>
                <td className="text-right p-2">{contract.oi?.toLocaleString() || 'N/A'}</td>
                <td className="text-right p-2">{contract.oi_change != null ? `${contract.oi_change > 0 ? '+' : ''}${contract.oi_change}%` : 'N/A'}</td>
                <td className="text-right p-2">{contract.volume?.toLocaleString() || 'N/A'}</td>
                <td className="text-right p-2">{contract.iv ? (contract.iv * 100).toFixed(2) + '%' : 'N/A'}</td>
                <td className="text-right p-2">{contract.delta != null ? contract.delta.toFixed(3) : 'N/A'}</td>
                <td className="text-right p-2">{contract.gamma ? contract.gamma.toFixed(4) : 'N/A'}</td>
                <td className="text-right p-2">{contract.vega ? contract.vega.toFixed(2) : 'N/A'}</td>
                <td className="text-right p-2">{contract.theta ? contract.theta.toFixed(2) : 'N/A'}</td>
                <td className="text-right p-2">{contract.liquidity_score?.toFixed(0) || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
