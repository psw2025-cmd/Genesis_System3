import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

export default function RiskDashboard() {
  const [riskMetrics, setRiskMetrics] = useState<any>(null)
  const [limitCheck, setLimitCheck] = useState<any>(null)

  useEffect(() => {
    const fetchRiskData = async () => {
      try {
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
          position_count: state.positions?.length || 0
        }
        
        // Check limits
        const limitsRes = await axios.post(`${API_BASE}/api/risk/check-limits`, {
          max_positions: 5,
          max_exposure: 100000,
          max_loss: -5000,
          max_concentration_pct: 50
        })
        
        setRiskMetrics(riskMetricsData)
        setLimitCheck(limitsRes.data.limit_check)
      } catch (error) {
        console.error('Error fetching risk data:', error)
        // Fallback to old endpoints
        try {
          const [riskRes, limitsRes] = await Promise.all([
            axios.get(`${API_BASE}/api/risk/portfolio`),
            axios.post(`${API_BASE}/api/risk/check-limits`, {
              max_positions: 5,
              max_exposure: 100000,
              max_loss: -5000,
              max_concentration_pct: 50
            })
          ])
          setRiskMetrics(riskRes.data.risk_metrics)
          setLimitCheck(limitsRes.data.limit_check)
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError)
        }
      }
    }

    fetchRiskData()
    // Optimized polling: 5000ms (5 seconds) - already optimal
    const interval = setInterval(fetchRiskData, 5000)
    return () => clearInterval(interval)
  }, [])

  if (!riskMetrics) {
    return <div className="p-6">Loading risk metrics...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Risk Management Dashboard</h2>

      {/* Risk Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Value at Risk (95%)</div>
          <div className={`text-2xl font-bold ${riskMetrics.var_95 < 0 ? 'text-red-400' : 'text-green-400'}`}>
            ₹{riskMetrics.var_95?.toFixed(2) || '0.00'}
          </div>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Expected Shortfall (95%)</div>
          <div className={`text-2xl font-bold ${riskMetrics.expected_shortfall_95 < 0 ? 'text-red-400' : 'text-green-400'}`}>
            ₹{riskMetrics.expected_shortfall_95?.toFixed(2) || '0.00'}
          </div>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Total Exposure</div>
          <div className="text-2xl font-bold">
            ₹{riskMetrics.total_exposure?.toFixed(2) || '0.00'}
          </div>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">Concentration Risk</div>
          <div className={`text-2xl font-bold ${riskMetrics.concentration_risk > 50 ? 'text-red-400' : 'text-yellow-400'}`}>
            {riskMetrics.concentration_risk?.toFixed(1) || '0'}%
          </div>
        </div>
      </div>

      {/* Greeks Exposure */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Greeks Exposure</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-400">Delta</div>
            <div className="text-2xl font-bold">{riskMetrics.greeks_exposure?.delta?.toFixed(4) || '0'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Gamma</div>
            <div className="text-2xl font-bold">{riskMetrics.greeks_exposure?.gamma?.toFixed(4) || '0'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Theta</div>
            <div className="text-2xl font-bold">{riskMetrics.greeks_exposure?.theta?.toFixed(4) || '0'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Vega</div>
            <div className="text-2xl font-bold">{riskMetrics.greeks_exposure?.vega?.toFixed(4) || '0'}</div>
          </div>
        </div>
      </div>

      {/* Risk Limits Status */}
      {limitCheck && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Risk Limits Status</h3>
          <div className={`p-4 rounded ${limitCheck.status === 'PASS' ? 'bg-green-900' : 'bg-red-900'}`}>
            <div className="text-lg font-bold mb-2">
              Status: {limitCheck.status}
            </div>
            {limitCheck.breaches && limitCheck.breaches.length > 0 && (
              <div className="mt-2">
                <div className="text-red-400 font-bold">Breaches:</div>
                {limitCheck.breaches.map((b: any, idx: number) => (
                  <div key={idx} className="text-sm">
                    {b.limit}: {b.value} (Limit: {b.limit_value})
                  </div>
                ))}
              </div>
            )}
            {limitCheck.warnings && limitCheck.warnings.length > 0 && (
              <div className="mt-2">
                <div className="text-yellow-400 font-bold">Warnings:</div>
                {limitCheck.warnings.map((w: any, idx: number) => (
                  <div key={idx} className="text-sm">
                    {w.limit}: {w.value} (Limit: {w.limit_value})
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Underlying Exposures */}
      {riskMetrics.underlying_exposures && Object.keys(riskMetrics.underlying_exposures).length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Exposure by Underlying</h3>
          <div className="space-y-2">
            {Object.entries(riskMetrics.underlying_exposures).map(([underlying, exposure]: [string, any]) => (
              <div key={underlying} className="flex justify-between">
                <span>{underlying}</span>
                <span className="font-bold">₹{exposure.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
