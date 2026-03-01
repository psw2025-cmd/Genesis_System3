import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, Legend } from 'recharts'
import { Shield, AlertTriangle, Activity, PieChart as PieIcon } from 'lucide-react'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8']

export default function RiskDashboard() {
  const [riskMetrics, setRiskMetrics] = useState<any>(null)
  const [limitCheck, setLimitCheck] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRiskData = async () => {
      try {
        setLoading(true)
        // Use SSOT for consistency
        const stateRes = await axios.get(`${API_BASE}/api/state`)
        const state = stateRes.data
        
        // Use risk data from SSOT
        const riskData = state.risk || {}
        const riskMetricsData = {
          var_95: riskData.var95 || 0,
          expected_shortfall_95: riskData.es95 || 0,
          total_exposure: riskData.exposure || 0,
          concentration_risk: riskData.concentration || 0,
          total_pnl: state.pnl?.total || 0,
          position_count: state.positions?.length || 0,
          greeks_exposure: riskData.greeks || riskData.greeks_exposure || { delta: 0, gamma: 0, theta: 0, vega: 0 },
          underlying_exposures: riskData.underlying_exposures || {}
        }
        
        setRiskMetrics(riskMetricsData)
        
        // Try limits check
        try {
          const limitsRes = await axios.post(`${API_BASE}/api/risk/check-limits`, {
            max_positions: 5,
            max_exposure: 100000,
            max_loss: -5000,
            max_concentration_pct: 50
          })
          setLimitCheck(limitsRes.data?.limit_check || null)
        } catch {
          setLimitCheck(riskData.limits || { status: 'PASS', breaches: [], warnings: [] })
        }
      } catch (error) {
        console.error('Error fetching risk data:', error)
        // Fallback
        try {
          const [riskRes, limitsRes] = await Promise.all([
            axios.get(`${API_BASE}/api/risk/portfolio`),
            axios.post(`${API_BASE}/api/risk/check-limits`, { max_positions: 5, max_exposure: 100000 })
          ])
          setRiskMetrics(riskRes.data?.risk_metrics || riskRes.data)
          setLimitCheck(limitsRes.data?.limit_check || null)
        } catch (fbError) {
           setRiskMetrics(null)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchRiskData()
    const interval = setInterval(fetchRiskData, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !riskMetrics) {
    return <div className="p-12 text-center text-gray-500">Loading risk metrics...</div>
  }

  if (!riskMetrics) {
    return (
        <div className="p-12 text-center text-red-400 border border-red-900 bg-red-900/10 rounded-lg m-6">
            <AlertTriangle className="mx-auto h-12 w-12 mb-4" />
            <h3 className="text-xl font-bold">Risk Data Unavailable</h3>
            <p className="mt-2">Ensure the backend is running and connected to a broker or synthetic source.</p>
        </div>
    )
  }

  // Prepare chart data
  const underlyingData = Object.entries(riskMetrics.underlying_exposures || {}).map(([name, value]: [string, any]) => ({
    name, value
  })).filter(d => d.value > 0)

  const greeksData = [
    { name: 'Delta', value: riskMetrics.greeks_exposure?.delta || 0 },
    { name: 'Gamma', value: riskMetrics.greeks_exposure?.gamma || 0 },
    { name: 'Theta', value: riskMetrics.greeks_exposure?.theta || 0 },
    { name: 'Vega', value: riskMetrics.greeks_exposure?.vega || 0 }
  ]

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center border-b border-gray-700 pb-4">
        <div>
           <h2 className="text-3xl font-bold flex items-center gap-3">
             <Shield className="text-green-500" />
             Risk Management Dashboard
           </h2>
           <p className="text-gray-400 mt-1">Real-time portfolio risk monitoring and limit enforcement</p>
        </div>
        <div className={`px-4 py-2 rounded-lg font-bold border ${limitCheck?.status === 'PASS' ? 'bg-green-900/30 border-green-500 text-green-400' : 'bg-red-900/30 border-red-500 text-red-400'}`}>
            Limits Status: {limitCheck?.status || 'UNKNOWN'}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <div className="text-sm text-gray-400">Value at Risk (95%)</div>
          <div className={`text-3xl font-bold mt-2 ${riskMetrics.var_95 < -1000 ? 'text-red-400' : 'text-white'}`}>
            ₹{Math.abs(riskMetrics.var_95 || 0).toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Potential daily loss</div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <div className="text-sm text-gray-400">Expected Shortfall (95%)</div>
          <div className={`text-3xl font-bold mt-2 ${riskMetrics.expected_shortfall_95 < -2000 ? 'text-red-500' : 'text-white'}`}>
            ₹{Math.abs(riskMetrics.expected_shortfall_95 || 0).toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Tail risk exposure</div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <div className="text-sm text-gray-400">Total Exposure</div>
          <div className="text-3xl font-bold mt-2 text-blue-400">
            ₹{riskMetrics.total_exposure?.toLocaleString() || '0'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Gross market value</div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <div className="text-sm text-gray-400">Concentration Risk</div>
          <div className={`text-3xl font-bold mt-2 ${riskMetrics.concentration_risk > 50 ? 'text-orange-400' : 'text-green-400'}`}>
            {riskMetrics.concentration_risk?.toFixed(1) || '0'}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Max single asset exposure</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Greeks Exposure Chart */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Activity className="text-purple-400" />
            Portfolio Greeks
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={greeksData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={true} />
                <XAxis type="number" stroke="#9CA3AF" fontSize={10} />
                <YAxis dataKey="name" type="category" stroke="#9CA3AF" fontSize={12} width={60} />
                <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.5rem' }}
                    itemStyle={{ color: '#E5E7EB' }}
                />
                <Bar dataKey="value" fill="#8B5CF6" radius={[0, 4, 4, 0]}>
                    {greeksData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#10B981' : '#EF4444'} />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Underlying Exposure Pie Chart */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <PieIcon className="text-blue-400" />
            Exposure Allocation
          </h3>
          {underlyingData.length > 0 ? (
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={underlyingData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                    >
                        {underlyingData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip 
                        contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.5rem' }}
                        itemStyle={{ color: '#E5E7EB' }}
                        formatter={(value: number) => `₹${value.toLocaleString()}`}
                    />
                    <Legend />
                </PieChart>
                </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-gray-500 bg-gray-900/50 rounded-lg">
                <PieIcon className="w-12 h-12 mb-2 opacity-20" />
                <p>No active positions</p>
            </div>
          )}
        </div>
      </div>

      {/* Risk Limits Detail */}
      {limitCheck && (limitCheck.breaches?.length > 0 || limitCheck.warnings?.length > 0) && (
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <AlertTriangle className="text-yellow-500" />
            Risk Alerts
          </h3>
          <div className="space-y-3">
             {limitCheck.breaches?.map((b: any, idx: number) => (
               <div key={`breach-${idx}`} className="flex items-center gap-3 bg-red-900/20 border border-red-500/30 p-3 rounded-lg text-red-200">
                 <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
                 <div>
                   <span className="font-bold">CRITICAL BREACH:</span> {b.limit} is {b.value} (Limit: {b.limit_value})
                 </div>
               </div>
             ))}
             {limitCheck.warnings?.map((w: any, idx: number) => (
               <div key={`warn-${idx}`} className="flex items-center gap-3 bg-yellow-900/20 border border-yellow-500/30 p-3 rounded-lg text-yellow-200">
                 <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0" />
                 <div>
                   <span className="font-bold">WARNING:</span> {w.limit} is {w.value} (Limit: {w.limit_value})
                 </div>
               </div>
             ))}
          </div>
        </div>
      )}
    </div>
  )
}
