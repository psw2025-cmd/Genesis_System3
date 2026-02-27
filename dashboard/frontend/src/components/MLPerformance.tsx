import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

export default function MLPerformance() {
  const [performance, setPerformance] = useState<any>(null)
  const [comparison, setComparison] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [perfRes, compRes] = await Promise.allSettled([
          axios.get(`${API_BASE}/api/ml/performance`, { timeout: 5000 }),
          axios.get(`${API_BASE}/api/ml/compare`, { timeout: 5000 })
        ])
        
        if (perfRes.status === 'fulfilled') {
          setPerformance(perfRes.value.data.performance || perfRes.value.data)
        } else {
          console.warn('ML performance fetch failed:', perfRes.reason?.message)
          setPerformance(null)
        }
        
        if (compRes.status === 'fulfilled') {
          setComparison(compRes.value.data.comparison || compRes.value.data)
        } else {
          console.warn('ML comparison fetch failed:', compRes.reason?.message)
          setComparison(null)
        }
      } catch (error) {
        console.error('Error fetching ML performance:', error)
        setPerformance(null)
        setComparison(null)
      }
    }

    fetchData()
    // Optimized polling: 10000ms (10 seconds) - ML metrics don't need frequent updates
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  // Use SSOT for model status if available
  const [state, setState] = useState<any>(null)
  
  useEffect(() => {
    const fetchState = async () => {
      try {
        const stateRes = await axios.get(`${API_BASE}/api/state`)
        setState(stateRes.data)
      } catch (error) {
        // Ignore if SSOT not available
      }
    }
    fetchState()
    const interval = setInterval(fetchState, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">ML Model Performance</h2>

      {/* Active Model from SSOT */}
      {state?.model && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Active Model</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-400">Model Name</div>
              <div className="text-lg font-bold">{state.model.active || 'Ensemble'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Model Type</div>
              <div className="text-lg">{state.model.type || 'Ensemble'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Fallback Used</div>
              <div className={`text-lg ${state.model.fallback_used ? 'text-yellow-400' : 'text-green-400'}`}>
                {state.model.fallback_used ? 'Yes' : 'No'}
              </div>
            </div>
          </div>
          {state.model.metrics && Object.keys(state.model.metrics).length > 0 && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(state.model.metrics).map(([key, value]: [string, any]) => (
                <div key={key}>
                  <div className="text-sm text-gray-400">{key}</div>
                  <div className="text-lg">{typeof value === 'number' ? value.toFixed(4) : value}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Model Comparison */}
      {comparison && comparison.models && Object.keys(comparison.models).length > 0 ? (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Model Comparison</h3>
          {comparison.best_model && (
            <div className="mb-4 p-3 bg-green-900 rounded">
              <div className="font-bold">Best Model: {comparison.best_model.name || 'N/A'}</div>
              <div className="text-sm">
                Accuracy: {comparison.best_model.metrics?.avg_accuracy ? (comparison.best_model.metrics.avg_accuracy * 100).toFixed(2) + '%' : 'N/A'}
              </div>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(comparison.models).map(([name, metrics]: [string, any]) => (
              <div key={name} className="bg-gray-700 p-4 rounded">
                <div className="font-bold mb-2">{name}</div>
                <div className="text-sm space-y-1">
                  <div>Accuracy: {metrics?.avg_accuracy ? (metrics.avg_accuracy * 100).toFixed(2) + '%' : 'N/A'}</div>
                  <div>Confidence: {metrics?.avg_confidence ? (metrics.avg_confidence * 100).toFixed(2) + '%' : 'N/A'}</div>
                  <div>Predictions: {metrics?.total_predictions || 0}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Model Comparison</h3>
          <div className="text-gray-400">
            No model comparison data available. Models will appear here once training data is available.
          </div>
        </div>
      )}

      {/* Individual Model Performance */}
      {performance && performance.models && Object.keys(performance.models).length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">All Models</h3>
          <div className="space-y-4">
            {Object.entries(performance.models).map(([name, metrics]: [string, any]) => (
              <div key={name} className="bg-gray-700 p-4 rounded">
                <div className="font-bold text-lg mb-2">{name}</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-gray-400">Total Predictions</div>
                    <div className="text-xl font-bold">{metrics?.total_predictions || 0}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Avg Accuracy</div>
                    <div className="text-xl font-bold">{metrics?.avg_accuracy ? (metrics.avg_accuracy * 100).toFixed(2) + '%' : 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Avg Confidence</div>
                    <div className="text-xl font-bold">{metrics?.avg_confidence ? (metrics.avg_confidence * 100).toFixed(2) + '%' : 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Underlyings</div>
                    <div className="text-xl font-bold">{metrics?.underlyings_count || 0}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!performance && !comparison && (
        <div className="text-gray-400 text-center py-12">
          No ML performance data available
        </div>
      )}
    </div>
  )
}
