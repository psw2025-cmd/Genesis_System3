import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts'

const UNDERLYINGS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

export default function AdvancedCharts() {
  const [selectedUnderlying, setSelectedUnderlying] = useState('NIFTY')
  const [heatmapData, setHeatmapData] = useState<any>(null)
  const [ivSurface, setIvSurface] = useState<any>(null)
  const [greeksData, setGreeksData] = useState<any>(null)
  const [pcrData, setPcrData] = useState<any>(null)
  const [selectedMetric, setSelectedMetric] = useState('oi')
  const [selectedGreek, setSelectedGreek] = useState('delta')

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const [heatmapRes, ivRes, greeksRes, pcrRes] = await Promise.all([
          axios.get(`${API_BASE}/api/charting/heatmap/${selectedUnderlying}?metric=${selectedMetric}`),
          axios.get(`${API_BASE}/api/charting/iv-surface/${selectedUnderlying}`),
          axios.get(`${API_BASE}/api/charting/greeks/${selectedUnderlying}?greek=${selectedGreek}`),
          axios.get(`${API_BASE}/api/charting/pcr/${selectedUnderlying}`)
        ])
        
        if (heatmapRes.data.status === 'ok') {
          setHeatmapData(heatmapRes.data.heatmap)
        } else {
          console.warn('Heatmap status not ok:', heatmapRes.data)
        }
        if (ivRes.data.status === 'ok') {
          setIvSurface(ivRes.data.surface)
        } else {
          console.warn('IV Surface status not ok:', ivRes.data)
        }
        if (greeksRes.data.status === 'ok') {
          setGreeksData(greeksRes.data.greeks)
        } else {
          console.warn('Greeks status not ok:', greeksRes.data)
        }
        if (pcrRes.data.status === 'ok') {
          setPcrData(pcrRes.data.pcr)
        } else {
          console.warn('PCR status not ok:', pcrRes.data)
        }
      } catch (error: any) {
        console.error('Error fetching chart data:', error)
        // Set empty data on error to prevent infinite loading
        if (!heatmapData) setHeatmapData(null)
        if (!ivSurface) setIvSurface(null)
        if (!greeksData) setGreeksData(null)
        if (!pcrData) setPcrData(null)
      }
    }

    fetchChartData()
    // Optimized polling: 10000ms (10 seconds) - charts don't need frequent updates
    const interval = setInterval(fetchChartData, 10000)
    return () => clearInterval(interval)
  }, [selectedUnderlying, selectedMetric, selectedGreek])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Advanced Charts</h2>
        <select
          value={selectedUnderlying}
          onChange={(e) => setSelectedUnderlying(e.target.value)}
          className="bg-gray-700 text-white px-4 py-2 rounded"
        >
          {UNDERLYINGS.map(u => (
            <option key={u} value={u}>{u}</option>
          ))}
        </select>
      </div>

      {/* Heatmap */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Option Chain Heatmap</h3>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="bg-gray-700 text-white px-3 py-1 rounded text-sm"
          >
            <option value="oi">Open Interest</option>
            <option value="volume">Volume</option>
            <option value="iv">Implied Volatility</option>
            <option value="ltp">Last Traded Price</option>
          </select>
        </div>
        {heatmapData ? (
          <div className="text-gray-300">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-sm text-gray-400">Strikes</div>
                <div className="text-xl font-bold">{heatmapData.strikes?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Expiries</div>
                <div className="text-xl font-bold">{heatmapData.expiries?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Spot Price</div>
                <div className="text-xl font-bold">₹{heatmapData.spot?.toFixed(2) || '0.00'}</div>
              </div>
            </div>
            {heatmapData.heatmap && heatmapData.heatmap.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">Heatmap Visualization:</div>
                <div className="bg-gray-900 p-4 rounded h-64 overflow-auto">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={heatmapData.heatmap.slice(0, 10).map((exp: any, idx: number) => ({
                      expiry: exp.expiry,
                      maxOI: Math.max(...(exp.values || [0])),
                      avgOI: exp.values ? exp.values.reduce((a: number, b: number) => a + b, 0) / exp.values.length : 0
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="expiry" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      <Legend />
                      <Bar dataKey="maxOI" fill="#3B82F6" name="Max OI" />
                      <Bar dataKey="avgOI" fill="#10B981" name="Avg OI" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Showing {Math.min(10, heatmapData.heatmap.length)} of {heatmapData.heatmap.length} expiries
                </div>
              </div>
            )}
            <p className="text-sm text-green-400 mt-2">✓ Heatmap data loaded successfully</p>
          </div>
        ) : (
          <div className="text-gray-400">Loading heatmap data...</div>
        )}
      </div>

      {/* IV Surface */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">IV Surface</h3>
        {ivSurface ? (
          <div className="text-gray-300">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-sm text-gray-400">Strikes</div>
                <div className="text-xl font-bold">{ivSurface.strikes?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Expiries</div>
                <div className="text-xl font-bold">{ivSurface.expiries?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Spot Price</div>
                <div className="text-xl font-bold">₹{ivSurface.spot?.toFixed(2) || '0.00'}</div>
              </div>
            </div>
            <p className="text-sm text-green-400 mt-2">✓ IV surface data loaded successfully</p>
          </div>
        ) : (
          <div className="text-gray-400">Loading IV surface data...</div>
        )}
      </div>

      {/* Greeks Chart */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Greeks Chart</h3>
          <select
            value={selectedGreek}
            onChange={(e) => setSelectedGreek(e.target.value)}
            className="bg-gray-700 text-white px-3 py-1 rounded text-sm"
          >
            <option value="delta">Delta</option>
            <option value="gamma">Gamma</option>
            <option value="theta">Theta</option>
            <option value="vega">Vega</option>
          </select>
        </div>
        {greeksData ? (
          <div className="text-gray-300">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-sm text-gray-400">Greek</div>
                <div className="text-xl font-bold capitalize">{greeksData.greek || selectedGreek}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Strikes</div>
                <div className="text-xl font-bold">{greeksData.strikes?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Spot Price</div>
                <div className="text-xl font-bold">₹{greeksData.spot?.toFixed(2) || '0.00'}</div>
              </div>
            </div>
            {greeksData.values && greeksData.values.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">{selectedGreek.toUpperCase()} Chart:</div>
                <div className="bg-gray-900 p-4 rounded h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={greeksData.values.slice(0, 20).map((val: number, idx: number) => ({
                      strike: greeksData.strikes?.[idx] || idx,
                      value: val
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="strike" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      <Bar dataKey="value" fill="#8B5CF6" name={selectedGreek.toUpperCase()} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
            <p className="text-sm text-green-400 mt-2">✓ Greeks data loaded successfully</p>
          </div>
        ) : (
          <div className="text-gray-400">Loading Greeks data...</div>
        )}
      </div>

      {/* PCR Chart */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Put-Call Ratio</h3>
        {pcrData ? (
          <div className="text-gray-300">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-sm text-gray-400">Overall PCR</div>
                <div className={`text-xl font-bold ${
                  pcrData.overall_pcr > 1.0 ? 'text-red-400' : 
                  pcrData.overall_pcr > 0.8 ? 'text-yellow-400' : 'text-green-400'
                }`}>
                  {pcrData.overall_pcr?.toFixed(2) || '0.00'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Strikes</div>
                <div className="text-xl font-bold">{pcrData.strikes?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Spot Price</div>
                <div className="text-xl font-bold">₹{pcrData.spot?.toFixed(2) || '0.00'}</div>
              </div>
            </div>
            {pcrData.strikes && pcrData.strikes.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">PCR by Strike:</div>
                <div className="bg-gray-900 p-4 rounded h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={pcrData.strikes.slice(0, 20).map((strike: number, idx: number) => ({
                      strike: strike,
                      pcr: pcrData.pcr_by_strike?.[idx] || pcrData.overall_pcr || 0
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="strike" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      <Bar dataKey="pcr" fill="#F59E0B" name="PCR">
                        {pcrData.strikes.slice(0, 20).map((_: any, idx: number) => {
                          const pcr = pcrData.pcr_by_strike?.[idx] || pcrData.overall_pcr || 0
                          return <Cell key={idx} fill={pcr > 1.0 ? '#EF4444' : pcr > 0.8 ? '#F59E0B' : '#10B981'} />
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
            <p className="text-sm text-green-400 mt-2">✓ PCR data loaded successfully</p>
          </div>
        ) : (
          <div className="text-gray-400">Loading PCR data...</div>
        )}
      </div>
    </div>
  )
}
