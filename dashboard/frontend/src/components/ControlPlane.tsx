import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import EmptyState from './EmptyState'
import ErrorBanner from './ErrorBanner'

export default function ControlPlane() {
  const [refreshInterval, setRefreshInterval] = useState(5)
  const [status, setStatus] = useState('')
  const [runnerStatus, setRunnerStatus] = useState<any>(null)
  const [learningStatus, setLearningStatus] = useState<any>(null)
  const [learningInsights, setLearningInsights] = useState<any>(null)
  const [forensicReport, setForensicReport] = useState<any>(null)
  const [validationStatus, setValidationStatus] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [errors, setErrors] = useState<Array<{endpoint: string, status?: number, message: string}>>([])

  useEffect(() => {
    fetchAllData()
    const interval = setInterval(fetchAllData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchAllData = async () => {
    try {
      const [runnerStatusRes, learningStatusRes, learningInsightsRes, forensicRes, validationRes] = await Promise.allSettled([
        axios.get(`${API_BASE}/api/runner/status`),
        axios.get(`${API_BASE}/api/learning/status`),
        axios.get(`${API_BASE}/api/learning/insights`),
        axios.get(`${API_BASE}/api/forensic/report`),
        axios.get(`${API_BASE}/api/validation/status`)
      ])

      const newErrors: Array<{endpoint: string, status?: number, message: string}> = []
      
      if (runnerStatusRes.status === 'fulfilled') {
        setRunnerStatus(runnerStatusRes.value.data)
      } else {
        const reason = runnerStatusRes.reason
        newErrors.push({
          endpoint: `${API_BASE}/api/runner/status`,
          status: reason?.response?.status,
          message: reason?.message || 'Failed to fetch runner status'
        })
        console.error('Error fetching runner status:', reason)
      }
      
      if (learningStatusRes.status === 'fulfilled') {
        setLearningStatus(learningStatusRes.value.data)
      } else {
        const reason = learningStatusRes.reason
        newErrors.push({
          endpoint: `${API_BASE}/api/learning/status`,
          status: reason?.response?.status,
          message: reason?.message || 'Failed to fetch learning status'
        })
        console.error('Error fetching learning status:', reason)
      }
      
      if (learningInsightsRes.status === 'fulfilled') {
        setLearningInsights(learningInsightsRes.value.data)
      } else {
        const reason = learningInsightsRes.reason
        newErrors.push({
          endpoint: `${API_BASE}/api/learning/insights`,
          status: reason?.response?.status,
          message: reason?.message || 'Failed to fetch learning insights'
        })
        console.error('Error fetching learning insights:', reason)
      }
      
      if (forensicRes.status === 'fulfilled') {
        setForensicReport(forensicRes.value.data)
      } else {
        const reason = forensicRes.reason
        newErrors.push({
          endpoint: `${API_BASE}/api/forensic/report`,
          status: reason?.response?.status,
          message: reason?.message || 'Failed to fetch forensic report'
        })
        console.error('Error fetching forensic report:', reason)
      }
      
      if (validationRes.status === 'fulfilled') {
        setValidationStatus(validationRes.value.data)
      } else {
        const reason = validationRes.reason
        newErrors.push({
          endpoint: `${API_BASE}/api/validation/status`,
          status: reason?.response?.status,
          message: reason?.message || 'Failed to fetch validation status'
        })
        console.error('Error fetching validation status:', reason)
      }
      
      setErrors(newErrors)
    } catch (error) {
      console.error('Error fetching control data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStart = async () => {
    setLoading(true)
    setStatus('Starting runner...')
    try {
      const res = await axios.post(`${API_BASE}/api/runner/start`, {
        refresh: refreshInterval,
        live: false  // Always PAPER mode
      })
      if (res.data.success) {
        setStatus(`✅ Runner started (PID: ${res.data.pid || 'N/A'}, Mode: ${res.data.mode || 'PAPER'})`)
      } else {
        setStatus(`❌ Failed: ${res.data.error || res.data.message || 'Unknown error'}`)
      }
      setTimeout(() => {
        fetchAllData()
        setStatus('')
      }, 2000)
    } catch (error: any) {
      setStatus(`❌ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    setStatus('Stopping runner...')
    try {
      const res = await axios.post(`${API_BASE}/api/runner/stop`)
      if (res.data.success) {
        setStatus(`✅ Runner stopped (${res.data.stopped || 0} process(es))`)
      } else {
        setStatus(`❌ Failed: ${res.data.error || 'Unknown error'}`)
      }
      setTimeout(() => {
        fetchAllData()
        setStatus('')
      }, 2000)
    } catch (error: any) {
      setStatus(`❌ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRunLearning = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/learning/run`)
      setStatus(`Learning cycle: ${res.data.success ? 'Completed' : 'Failed'}`)
      setTimeout(() => fetchAllData(), 2000)
    } catch (error: any) {
      setStatus(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRunForensic = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/forensic/run`)
      setStatus(`Forensic analysis: ${res.data.success ? 'Completed' : 'Failed'}`)
      setTimeout(() => fetchAllData(), 2000)
    } catch (error: any) {
      setStatus(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRunValidation = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/validation/run`)
      setStatus(`Validation: ${res.data.success ? 'Completed' : 'Failed'}`)
      setTimeout(() => fetchAllData(), 2000)
    } catch (error: any) {
      setStatus(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Control Plane</h2>
        <div className="p-6 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-xl font-bold">Loading control systems...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Control Plane</h2>

      {/* Show errors if any */}
      {errors.length > 0 && (
        <div className="space-y-2">
          {errors.map((err, idx) => (
            <ErrorBanner
              key={idx}
              endpoint={err.endpoint}
              status={err.status}
              message={err.message}
            />
          ))}
        </div>
      )}

      {/* Show empty state if no data and no errors */}
      {!learningStatus && !learningInsights && !forensicReport && !validationStatus && errors.length === 0 && (
        <EmptyState
          title="Control systems not initialized"
          reason="Learning, Forensic, and Validation systems are not yet initialized. Use the buttons below to run them."
          icon="⚙️"
        />
      )}

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">System Controls</h3>
        <div className="space-y-4">
          {/* Runner Status Display */}
          {runnerStatus && (
            <div className="bg-gray-900 p-4 rounded mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold">Runner Status:</span>
                <span className={`px-3 py-1 rounded text-sm font-bold ${
                  runnerStatus.runner === 'RUNNING' ? 'bg-green-600 text-white' :
                  runnerStatus.runner === 'STOPPED' ? 'bg-gray-600 text-white' :
                  'bg-red-600 text-white'
                }`}>
                  {runnerStatus.runner || 'UNKNOWN'}
                </span>
              </div>
              {runnerStatus.runner === 'RUNNING' && (
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mt-2">
                  <div>Mode: <span className="text-white">{runnerStatus.mode || 'UNKNOWN'}</span></div>
                  <div>PID: <span className="text-white">{runnerStatus.pid || 'N/A'}</span></div>
                  {runnerStatus.heartbeat_age_seconds !== undefined && (
                    <div>Heartbeat: <span className="text-white">{runnerStatus.heartbeat_age_seconds}s ago</span></div>
                  )}
                  {runnerStatus.autopilot_running !== undefined && (
                    <div>Autopilot: <span className="text-white">{runnerStatus.autopilot_running ? 'ON' : 'OFF'}</span></div>
                  )}
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm mb-2">Refresh Interval (seconds)</label>
            <input
              type="number"
              min="1"
              max="60"
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="w-32 px-3 py-2 bg-gray-700 rounded"
            />
            <div className="text-xs text-gray-400 mt-1">Min: 1s, Max: 60s</div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleStart}
              disabled={loading || (runnerStatus?.runner === 'RUNNING')}
              className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Starting...' : 'Start Runner'}
            </button>
            <button
              onClick={handleStop}
              disabled={loading || (runnerStatus?.runner === 'STOPPED')}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Stopping...' : 'Stop Runner'}
            </button>
          </div>

          {status && (
            <div className={`text-sm p-2 rounded ${
              status.includes('✅') ? 'bg-green-900 text-green-200' :
              status.includes('❌') ? 'bg-red-900 text-red-200' :
              'bg-gray-700 text-gray-300'
            }`}>
              {status}
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Mode Selection</h3>
        <div className="space-y-2">
          <div>
            <label className="flex items-center">
              <input type="radio" name="mode" value="sim" className="mr-2" />
              Simulation Mode (with scenario selection)
            </label>
          </div>
          <div>
            <label className="flex items-center">
              <input type="radio" name="mode" value="live" className="mr-2" />
              Live Mode (trade execution disabled by default)
            </label>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Proof Pack</h3>
        <button
          onClick={() => {
            // Implementation would generate proof pack
            alert('Proof pack generation not implemented in UI - use scripts/verify_dashboard.ps1')
          }}
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
        >
          Download Proof Pack
        </button>
      </div>

      {/* Learning System */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Continuous Learning System</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span>Status:</span>
            <span className={learningStatus?.status === 'active' ? 'text-green-400' : 'text-gray-400'}>
              {learningStatus?.status || 'Not Available'}
            </span>
          </div>
          {learningInsights && (learningInsights.win_rate !== undefined || learningStatus?.latest_insights) && (
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span>Win Rate:</span>
                <span className={`font-bold ${
                  (learningInsights.win_rate || learningStatus?.latest_insights?.win_rate || 0) >= 0.65 ? 'text-green-400' :
                  (learningInsights.win_rate || learningStatus?.latest_insights?.win_rate || 0) >= 0.50 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {((learningInsights.win_rate || learningStatus?.latest_insights?.win_rate || 0) * 100).toFixed(2)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Total Trades:</span>
                <span className="font-bold text-white">
                  {learningInsights.total_trades || learningStatus?.latest_insights?.total_trades || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Best Strategy:</span>
                <span className="text-white">
                  {learningInsights.best_strategy || learningStatus?.latest_insights?.best_strategy || 'N/A'}
                </span>
              </div>
              {learningStatus?.total_cycles && (
                <div className="text-xs text-gray-400 mt-2">
                  Learning Cycles: {learningStatus.total_cycles}
                </div>
              )}
            </div>
          )}
          <button
            onClick={handleRunLearning}
            disabled={loading}
            className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Learning Cycle'}
          </button>
        </div>
      </div>

      {/* Forensic Analysis */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Forensic Analysis</h3>
        <div className="space-y-4">
          {forensicReport && forensicReport.signal_accuracy && (
            <div className="space-y-2 text-sm">
              <div>Signal Accuracy: {(forensicReport.signal_accuracy.accuracy * 100).toFixed(2)}%</div>
              <div>Total Trades: {forensicReport.performance_metrics?.total_trades || 0}</div>
              <div>Win Rate: {(forensicReport.performance_metrics?.win_rate * 100).toFixed(2)}%</div>
              <div>Data Issues: {forensicReport.data_integrity?.issues?.length || 0}</div>
            </div>
          )}
          <button
            onClick={handleRunForensic}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 rounded hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Forensic Analysis'}
          </button>
        </div>
      </div>

      {/* Validation System */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Validation System</h3>
        <div className="space-y-4">
          {validationStatus && validationStatus.results && (
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span>Tests Passed:</span>
                <span className={`font-bold ${
                  validationStatus.results.success_rate >= 80 ? 'text-green-400' :
                  validationStatus.results.success_rate >= 50 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {validationStatus.results.tests_passed || 0}/{validationStatus.results.total_tests || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Success Rate:</span>
                <span className={`font-bold ${
                  validationStatus.results.success_rate >= 80 ? 'text-green-400' :
                  validationStatus.results.success_rate >= 50 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {(validationStatus.results.success_rate || 0).toFixed(1)}%
                </span>
              </div>
              {validationStatus.status && (
                <div className="text-xs text-gray-400 mt-2">
                  Status: {validationStatus.status}
                </div>
              )}
            </div>
          )}
          <button
            onClick={handleRunValidation}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Validation'}
          </button>
        </div>
      </div>

      {status && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="text-sm text-gray-400">{status}</div>
        </div>
      )}
    </div>
  )
}
