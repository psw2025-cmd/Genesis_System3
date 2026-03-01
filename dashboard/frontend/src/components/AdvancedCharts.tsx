import React, { useState, useEffect, useMemo } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell, ComposedChart, Line } from 'recharts'
import { AlertCircle, ArrowUpRight, TrendingUp, Activity, Layers } from 'lucide-react'

const UNDERLYINGS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

// Helper: Heatmap Grid Component
const HeatmapGrid = ({ title, data, xAxis, yAxis, valueKey = 'values', colorScale = 'blue', spot = 0 }: any) => {
  if (!data || !xAxis || !yAxis) return null

  // Find max value for normalization
  const maxValue = useMemo(() => {
    let max = 0
    data.forEach((row: any) => {
      if (row[valueKey]) {
        row[valueKey].forEach((val: number) => {
          if (val > max) max = val
        })
      }
    })
    return max
  }, [data, valueKey])

  // Generate color
  const getColor = (value: number) => {
    if (value === 0) return 'transparent'
    const intensity = Math.max(0.1, value / (maxValue || 1))
    if (colorScale === 'blue') return `rgba(59, 130, 246, ${intensity})` // Blue-500
    if (colorScale === 'red') return `rgba(239, 68, 68, ${intensity})`   // Red-500
    if (colorScale === 'green') return `rgba(16, 185, 129, ${intensity})` // Green-500
    if (colorScale === 'purple') return `rgba(139, 92, 246, ${intensity})` // Purple-500
    return `rgba(255, 255, 255, ${intensity})`
  }

  // Find closest strike to spot
  const closestStrikeIndex = xAxis.reduce((prev: number, curr: number, index: number) => {
    return Math.abs(curr - spot) < Math.abs(xAxis[prev] - spot) ? index : prev
  }, 0)

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[800px]">
        <div className="grid grid-cols-[100px_1fr] gap-4">
          {/* Y-Axis Label */}
          <div className="flex items-center justify-center font-bold text-gray-400 -rotate-90">
            Expiries
          </div>
          
          <div>
            {/* X-Axis Labels (Strikes) */}
            <div className="flex mb-2">
              <div className="w-24 shrink-0"></div> {/* Spacer for row headers */}
              <div className="flex-1 flex justify-between px-2">
                {xAxis.map((strike: number, idx: number) => (
                  <div 
                    key={strike} 
                    className={`text-xs w-16 text-center shrink-0 ${idx === closestStrikeIndex ? 'text-yellow-400 font-bold bg-yellow-900/30 rounded' : 'text-gray-400'}`}
                  >
                    {strike}
                  </div>
                ))}
              </div>
            </div>

            {/* Grid */}
            <div className="space-y-1">
              {data.map((row: any, rowIdx: number) => (
                <div key={rowIdx} className="flex items-center">
                  {/* Row Header (Expiry) */}
                  <div className="w-24 text-xs text-gray-400 font-mono shrink-0">
                    {row.expiry || row.label}
                  </div>
                  
                  {/* Cells */}
                  <div className="flex-1 flex justify-between px-2 bg-gray-900/50 rounded p-1">
                    {row[valueKey].map((val: number, colIdx: number) => (
                      <div
                        key={`${rowIdx}-${colIdx}`}
                        className="w-16 h-8 flex items-center justify-center text-[10px] text-white/80 shrink-0 border border-gray-800/50 rounded-sm relative group"
                        style={{ backgroundColor: getColor(val) }}
                      >
                        {val > 0 ? (val > 1000 ? `${(val/1000).toFixed(1)}k` : val) : ''}
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-10 bg-black border border-gray-700 p-2 rounded text-xs whitespace-nowrap shadow-xl">
                          <div className="font-bold">{title}</div>
                          <div>Expiry: {row.expiry}</div>
                          <div>Strike: {xAxis[colIdx]}</div>
                          <div>Value: {val.toLocaleString()}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            {/* X-Axis Label */}
            <div className="text-center text-sm font-bold text-gray-400 mt-2">
              Strike Prices
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AdvancedCharts() {
  const [selectedUnderlying, setSelectedUnderlying] = useState('NIFTY')
  const [heatmapData, setHeatmapData] = useState<any>(null)
  const [ivSurface, setIvSurface] = useState<any>(null)
  const [greeksData, setGreeksData] = useState<any>(null)
  const [pcrData, setPcrData] = useState<any>(null)
  const [selectedMetric, setSelectedMetric] = useState('oi')
  const [selectedGreek, setSelectedGreek] = useState('delta')

  const [chartError, setChartError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setLoading(true)
        setChartError(null)
        const [heatmapRes, ivRes, greeksRes, pcrRes] = await Promise.all([
          axios.get(`${API_BASE}/api/charting/heatmap/${selectedUnderlying}?metric=${selectedMetric}`),
          axios.get(`${API_BASE}/api/charting/iv-surface/${selectedUnderlying}`),
          axios.get(`${API_BASE}/api/charting/greeks/${selectedUnderlying}?greek=${selectedGreek}`),
          axios.get(`${API_BASE}/api/charting/pcr/${selectedUnderlying}`)
        ])
        
        if (heatmapRes.data.status === 'ok') setHeatmapData(heatmapRes.data.heatmap)
        else setHeatmapData(null)
        
        if (ivRes.data.status === 'ok') setIvSurface(ivRes.data.surface)
        else setIvSurface(null)
        
        if (greeksRes.data.status === 'ok') setGreeksData(greeksRes.data.greeks)
        else setGreeksData(null)
        
        if (pcrRes.data.status === 'ok') setPcrData(pcrRes.data.pcr)
        else setPcrData(null)

      } catch (error: any) {
        console.error('Error fetching chart data:', error)
        setChartError(error.response?.data?.message || error.message || 'Failed to load chart data')
      } finally {
        setLoading(false)
      }
    }

    fetchChartData()
    const interval = setInterval(fetchChartData, 10000)
    return () => clearInterval(interval)
  }, [selectedUnderlying, selectedMetric, selectedGreek])

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center border-b border-gray-700 pb-4">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Activity className="text-blue-500" />
            Advanced Market Analysis
          </h2>
          <p className="text-gray-400 mt-1">Deep-dive into option chain structure, volatility, and risk metrics</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="bg-gray-800 px-4 py-2 rounded-lg border border-gray-700">
             <span className="text-sm text-gray-400 mr-2">Spot:</span>
             <span className="text-xl font-bold text-white">
               {heatmapData?.spot ? `₹${heatmapData.spot.toFixed(2)}` : '---'}
             </span>
          </div>
          
          <select
            aria-label="Select underlying index"
            value={selectedUnderlying}
            onChange={(e) => setSelectedUnderlying(e.target.value)}
            className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {UNDERLYINGS.map(u => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </div>
      </div>

      {chartError && (
        <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-red-500 shrink-0 mt-1" />
          <div>
            <div className="font-bold text-red-400">Analysis Unavailable</div>
            <div className="text-sm text-gray-300">{chartError}</div>
            <div className="text-xs text-gray-400 mt-1">Requires active market data or synthetic simulation.</div>
          </div>
        </div>
      )}

      {/* HEATMAP SECTION */}
      <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Layers className="text-purple-400" />
            Option Chain Heatmap
          </h3>
          <div className="flex items-center gap-2 bg-gray-900 p-1 rounded-lg border border-gray-700">
            {['oi', 'volume', 'iv', 'ltp'].map(m => (
              <button
                key={m}
                onClick={() => setSelectedMetric(m)}
                className={`px-3 py-1 text-sm rounded-md transition-all ${
                  selectedMetric === m 
                    ? 'bg-blue-600 text-white font-bold shadow-lg' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                {m.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {loading && !heatmapData ? (
          <div className="h-64 flex items-center justify-center text-gray-500">Loading heatmap data...</div>
        ) : heatmapData?.heatmap?.length > 0 ? (
          <HeatmapGrid 
            title={selectedMetric.toUpperCase()} 
            data={heatmapData.heatmap} 
            xAxis={heatmapData.strikes} 
            yAxis={heatmapData.expiries} 
            valueKey="values"
            colorScale={selectedMetric === 'oi' ? 'blue' : selectedMetric === 'volume' ? 'green' : 'purple'}
            spot={heatmapData.spot}
          />
        ) : (
          <div className="h-64 flex flex-col items-center justify-center text-gray-500 bg-gray-900/50 rounded-lg">
            <Layers className="w-12 h-12 mb-2 opacity-20" />
            <p>No heatmap data available</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* IV SURFACE */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <TrendingUp className="text-green-400" />
            Volatility Surface (IV)
          </h3>
          
          {ivSurface?.surface?.length > 0 ? (
            <HeatmapGrid 
              title="Implied Volatility" 
              data={ivSurface.surface} 
              xAxis={ivSurface.strikes} 
              yAxis={ivSurface.expiries} 
              valueKey="iv_values"
              colorScale="red"
              spot={ivSurface.spot}
            />
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-500 bg-gray-900/50 rounded-lg">
               No IV surface data
            </div>
          )}
        </div>

        {/* GREEKS & PCR */}
        <div className="space-y-8">
          {/* Greeks Chart */}
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Activity className="text-orange-400" />
                Greeks Exposure
              </h3>
              <select
                value={selectedGreek}
                onChange={(e) => setSelectedGreek(e.target.value)}
                className="bg-gray-700 text-white px-3 py-1 rounded-md text-sm border border-gray-600 outline-none"
              >
                <option value="delta">Delta</option>
                <option value="gamma">Gamma</option>
                <option value="theta">Theta</option>
                <option value="vega">Vega</option>
              </select>
            </div>
            
            {greeksData?.values?.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={greeksData.values.slice(0, 30).map((val: number, idx: number) => ({
                    strike: greeksData.strikes?.[idx] || idx,
                    value: val
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="strike" stroke="#9CA3AF" fontSize={10} />
                    <YAxis stroke="#9CA3AF" fontSize={10} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.5rem' }}
                      itemStyle={{ color: '#E5E7EB' }}
                    />
                    <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]} name={selectedGreek.toUpperCase()} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 bg-gray-900/50 rounded-lg">
                No Greeks data
              </div>
            )}
          </div>

          {/* PCR Chart */}
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <ArrowUpRight className="text-blue-400" />
                Put-Call Ratio Structure
              </h3>
              <div className={`px-3 py-1 rounded font-bold text-sm ${
                (pcrData?.overall_pcr || 0) > 1 ? 'bg-red-900/50 text-red-400' : 'bg-green-900/50 text-green-400'
              }`}>
                PCR: {pcrData?.overall_pcr?.toFixed(2) || '1.00'}
              </div>
            </div>

            {pcrData?.strikes?.length > 0 ? (
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={pcrData.strikes.slice(0, 30).map((strike: number, idx: number) => ({
                    strike: strike,
                    pcr: pcrData.pcr_by_strike?.[idx] || 0
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="strike" stroke="#9CA3AF" fontSize={10} />
                    <YAxis stroke="#9CA3AF" fontSize={10} domain={[0, 3]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.5rem' }}
                      itemStyle={{ color: '#E5E7EB' }}
                    />
                    <Line type="monotone" dataKey="pcr" stroke="#F59E0B" strokeWidth={2} dot={false} name="PCR" />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-gray-500 bg-gray-900/50 rounded-lg">
                No PCR data
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
