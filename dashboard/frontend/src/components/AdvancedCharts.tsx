import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts'

const UNDERLYINGS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']
const CHART_COLORS = ['#22d3ee', '#a78bfa', '#34d399', '#fbbf24', '#fb7185', '#60a5fa']

function chartNumber(value: unknown): number | null {
  if (value == null || value === '') return null
  const number = Number(value)
  return Number.isFinite(number) ? number : null
}

export default function AdvancedCharts() {
  const [selectedUnderlying, setSelectedUnderlying] = useState('NIFTY')
  const [heatmapData, setHeatmapData] = useState<any>(null)
  const [ivSurface, setIvSurface] = useState<any>(null)
  const [greeksData, setGreeksData] = useState<any>(null)
  const [pcrData, setPcrData] = useState<any>(null)
  const [selectedMetric, setSelectedMetric] = useState('oi')
  const [selectedGreek, setSelectedGreek] = useState('delta')
  const [chartError, setChartError] = useState('')

  const rawIvSurface = Array.isArray(ivSurface?.surface) ? ivSurface.surface : []
  const ivSeries = rawIvSurface.map((row: any, index: number) => ({
    key: String(row?.expiry || `Expiry ${index + 1}`),
    values: Array.isArray(row?.iv_values) ? row.iv_values : [],
  })).filter((series: any) => series.values.some((value: unknown) => {
    const number = chartNumber(value)
    return number != null && number > 0
  }))
  const ivStrikes = Array.isArray(ivSurface?.strikes) ? ivSurface.strikes : []
  const ivRows = ivStrikes.map((strike: unknown, index: number) => {
    const row: Record<string, number | string | null> = { strike: chartNumber(strike) ?? String(strike) }
    for (const series of ivSeries) {
      const value = chartNumber(series.values[index])
      if (value != null && value > 0) row[series.key] = value
    }
    return row
  }).filter((row: any) => ivSeries.some((series: any) => chartNumber(row[series.key]) != null))

  const heatmapRows = (Array.isArray(heatmapData?.heatmap) ? heatmapData.heatmap : [])
    .map((expiry: any) => {
      const values = Array.isArray(expiry?.values)
        ? expiry.values.map(chartNumber).filter((value: number | null): value is number => value != null)
        : []
      if (!values.length) return null
      return {
        expiry: expiry.expiry,
        maxValue: Math.max(...values),
        avgValue: values.reduce((sum: number, value: number) => sum + value, 0) / values.length,
      }
    })
    .filter((row: any) => row != null)

  const rawPcrValues = Array.isArray(pcrData?.pcr_data) && pcrData.pcr_data.length > 0
    ? pcrData.pcr_data
    : Array.isArray(pcrData?.pcr_by_strike) ? pcrData.pcr_by_strike : []
  const pcrRows = (Array.isArray(pcrData?.strikes) ? pcrData.strikes : [])
    .map((strike: unknown, index: number) => {
      const pcr = chartNumber(rawPcrValues[index])
      return pcr == null ? null : { strike: chartNumber(strike) ?? String(strike), pcr }
    })
    .filter((row: any) => row != null)
  const overallPcr = chartNumber(pcrData?.overall_pcr)

  const greekHasSideData = Array.isArray(greeksData?.ce_data) || Array.isArray(greeksData?.pe_data)
  const greekStrikes = Array.isArray(greeksData?.strikes) ? greeksData.strikes : []
  const greekRows = greekStrikes.map((strike: unknown, index: number) => ({
    strike: chartNumber(strike) ?? String(strike),
    CE: greekHasSideData ? chartNumber(greeksData?.ce_data?.[index]) : null,
    PE: greekHasSideData ? chartNumber(greeksData?.pe_data?.[index]) : null,
    Value: greekHasSideData ? null : chartNumber(greeksData?.values?.[index]),
  })).filter((row: any) => row.CE != null || row.PE != null || row.Value != null)

  useEffect(() => {
    let cancelled = false
    setHeatmapData(null)
    setIvSurface(null)
    setGreeksData(null)
    setPcrData(null)
    setChartError('')

    const fetchChartData = async () => {
      const [heatmapRes, ivRes, greeksRes, pcrRes] = await Promise.allSettled([
          axios.get(`${API_BASE}/api/charting/heatmap/${selectedUnderlying}?metric=${selectedMetric}`),
          axios.get(`${API_BASE}/api/charting/iv-surface/${selectedUnderlying}`),
          axios.get(`${API_BASE}/api/charting/greeks/${selectedUnderlying}?greek=${selectedGreek}`),
          axios.get(`${API_BASE}/api/charting/pcr/${selectedUnderlying}`)
      ])
      if (cancelled) return

      const heatmapPayload = heatmapRes.status === 'fulfilled' && heatmapRes.value.data?.status === 'ok' ? heatmapRes.value.data.heatmap : null
      const ivPayload = ivRes.status === 'fulfilled' && ivRes.value.data?.status === 'ok' ? ivRes.value.data.surface : null
      const greeksPayload = greeksRes.status === 'fulfilled' && greeksRes.value.data?.status === 'ok' ? greeksRes.value.data.greeks : null
      const pcrPayload = pcrRes.status === 'fulfilled' && pcrRes.value.data?.status === 'ok' ? pcrRes.value.data.pcr : null
      const heatmapOk = heatmapPayload != null
      const ivOk = ivPayload != null
      const greeksOk = greeksPayload != null
      const pcrOk = pcrPayload != null

      setHeatmapData(heatmapPayload)
      setIvSurface(ivPayload)
      setGreeksData(greeksPayload)
      setPcrData(pcrPayload)
      setChartError([heatmapOk, ivOk, greeksOk, pcrOk].every(Boolean) ? '' : 'Some chart data could not be retrieved. Retrying automatically.')
    }

    void fetchChartData()
    // Optimized polling: 10000ms (10 seconds) - charts don't need frequent updates
    const interval = setInterval(() => void fetchChartData(), 10000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
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
            {heatmapRows.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">Heatmap Visualization:</div>
                <div className="bg-gray-900 p-4 rounded h-64 overflow-auto">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={heatmapRows.slice(0, 10)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="expiry" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      <Legend />
                      <Bar dataKey="maxValue" fill="#3B82F6" name={`Max ${selectedMetric.toUpperCase()}`} />
                      <Bar dataKey="avgValue" fill="#10B981" name={`Avg ${selectedMetric.toUpperCase()}`} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Showing {Math.min(10, heatmapRows.length)} of {heatmapRows.length} expiries with usable data
                </div>
              </div>
            )}
            {heatmapRows.length ? (
              <p className="text-sm text-green-400 mt-2">{selectedMetric.toUpperCase()} observations available.</p>
            ) : (
              <div data-testid="heatmap-unavailable" className="chart-unavailable">No usable {selectedMetric.toUpperCase()} observations were returned for this chain.</div>
            )}
          </div>
        ) : chartError ? (
          <div className="chart-unavailable" role="status">{chartError}</div>
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
            {ivRows.length > 0 && ivSeries.length > 0 ? (
              <div data-testid="iv-surface-chart" className="mt-4">
                <div className="text-sm text-gray-400 mb-2">Implied volatility by strike and expiry:</div>
                <div className="bg-gray-900 p-4 rounded h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={ivRows}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="strike" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      <Legend />
                      {ivSeries.map((series: any, index: number) => (
                        <Line key={series.key} type="monotone" dataKey={series.key} name={series.key} stroke={CHART_COLORS[index % CHART_COLORS.length]} dot={false} connectNulls={false} />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              <div data-testid="iv-surface-unavailable" className="chart-unavailable">No usable implied-volatility observations were returned for this chain.</div>
            )}
          </div>
        ) : chartError ? (
          <div className="chart-unavailable" role="status">{chartError}</div>
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
            {greekRows.length > 0 ? (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">{selectedGreek.toUpperCase()} Chart:</div>
                <div className="bg-gray-900 p-4 rounded h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={greekRows.slice(0, 40)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="strike" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      {greekHasSideData ? <>
                        <Legend />
                        <Bar dataKey="CE" fill="#22d3ee" name={`CE ${selectedGreek.toUpperCase()}`} />
                        <Bar dataKey="PE" fill="#a78bfa" name={`PE ${selectedGreek.toUpperCase()}`} />
                      </> : <Bar dataKey="Value" fill="#8B5CF6" name={selectedGreek.toUpperCase()} />}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              <div data-testid="greeks-chart-unavailable" className="chart-unavailable">No usable {selectedGreek} observations were returned for this chain.</div>
            )}
          </div>
        ) : chartError ? (
          <div className="chart-unavailable" role="status">{chartError}</div>
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
                  overallPcr == null ? 'text-gray-400' :
                  overallPcr > 1.0 ? 'text-red-400' :
                  overallPcr > 0.8 ? 'text-yellow-400' : 'text-green-400'
                }`}>
                  {overallPcr == null ? '--' : overallPcr.toFixed(2)}
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
            {pcrRows.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">PCR by Strike:</div>
                <div className="bg-gray-900 p-4 rounded h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={pcrRows.slice(0, 20)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="strike" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                      <Bar dataKey="pcr" fill="#F59E0B" name="PCR">
                        {pcrRows.slice(0, 20).map((row: any, idx: number) => {
                          return <Cell key={idx} fill={row.pcr > 1.0 ? '#EF4444' : row.pcr > 0.8 ? '#F59E0B' : '#10B981'} />
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
            {pcrRows.length ? (
              <p className="text-sm text-green-400 mt-2">PCR observations available.</p>
            ) : (
              <div data-testid="pcr-chart-unavailable" className="chart-unavailable">No per-strike PCR observations were returned.</div>
            )}
          </div>
        ) : chartError ? (
          <div className="chart-unavailable" role="status">{chartError}</div>
        ) : (
          <div className="text-gray-400">Loading PCR data...</div>
        )}
      </div>
    </div>
  )
}
