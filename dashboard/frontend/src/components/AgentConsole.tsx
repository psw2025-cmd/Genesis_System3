import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

// Declare electronAPI for TypeScript
declare global {
  interface Window {
    electronAPI?: {
      getAgentMemory: () => Promise<any>
      saveAgentMemory: (tasks: any) => Promise<any>
      showNotification: (options: { title: string; body: string }) => Promise<any>
      downloadProofPack: () => Promise<any>
      getBackendStatus: () => Promise<any>
      controlBackend: (action: string) => Promise<any>
    }
  }
}

export default function AgentConsole() {
  const [agentMemory, setAgentMemory] = useState<any>(null)
  const [upgradePlan, setUpgradePlan] = useState<any>(null)
  const [testResults, setTestResults] = useState<any>(null)
  const [issues, setIssues] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchAgentData = async () => {
      try {
        // Try Electron API first
        if (window.electronAPI) {
          const memory = await window.electronAPI.getAgentMemory()
          setAgentMemory(memory)
        } else {
          // Fallback to HTTP API
          const res = await axios.get(`${API_BASE}/api/agent/memory`)
          setAgentMemory(res.data)
        }

        // Fetch upgrade plan
        const planRes = await axios.get(`${API_BASE}/api/agent/upgrade-plan`)
        if (planRes.data && planRes.data.status !== 'none') {
          setUpgradePlan(planRes.data)
        }

        // Fetch issues (with timeout handling)
        try {
          const issuesRes = await axios.get(`${API_BASE}/api/agent/issues`, { timeout: 5000 })
          setIssues(issuesRes.data.issues || [])
        } catch (error: any) {
          console.warn('Error fetching issues:', error)
          // Don't set error state, just use empty array
          setIssues([])
        }

        // Fetch test results
        if (upgradePlan) {
          const testRes = await axios.get(`${API_BASE}/api/agent/test-results/${upgradePlan.plan_id}`)
          setTestResults(testRes.data)
        }
      } catch (error) {
        console.error('Error fetching agent data:', error)
      }
    }

    fetchAgentData()
    const interval = setInterval(fetchAgentData, 10000) // Poll every 10 seconds
    return () => clearInterval(interval)
  }, [upgradePlan])

  const handleApplyUpgrade = async () => {
    if (!upgradePlan) return
    
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/agent/apply-upgrade`, {
        plan_id: upgradePlan.plan_id
      })
      
      if (res.data.success) {
        alert('Upgrade applied successfully!')
        setUpgradePlan(null)
        
        // Show notification if Electron
        if (window.electronAPI) {
          await window.electronAPI.showNotification({
            title: 'Upgrade Applied',
            body: 'System upgrade has been applied successfully'
          })
        }
      } else {
        alert(`Upgrade failed: ${res.data.message}`)
      }
    } catch (error: any) {
      alert(`Error applying upgrade: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRollback = async () => {
    if (!confirm('Rollback to previous version? This will undo the last upgrade.')) return
    
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/agent/rollback`)
      if (res.data.success) {
        alert('Rollback successful!')
      } else {
        alert(`Rollback failed: ${res.data.message}`)
      }
    } catch (error: any) {
      alert(`Error rolling back: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadProofPack = async () => {
    try {
      if (window.electronAPI) {
        const result = await window.electronAPI.downloadProofPack()
        if (result.success) {
          // Download via Electron
          window.open(`${API_BASE}/api/proof-pack`, '_blank')
        }
      } else {
        // Browser download
        window.open(`${API_BASE}/api/proof-pack`, '_blank')
      }
    } catch (error: any) {
      alert(`Error downloading proof pack: ${error.message}`)
    }
  }

  const handlePauseAgent = async () => {
    try {
      const res = await axios.post(`${API_BASE}/api/agent/pause`)
      alert(res.data.paused ? 'Agent paused' : 'Agent resumed')
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Agent Console</h2>
        <div className="flex gap-2">
          <button
            onClick={handleDownloadProofPack}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
          >
            Download Proof Pack
          </button>
          <button
            onClick={handlePauseAgent}
            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded"
          >
            Pause Agent
          </button>
        </div>
      </div>

      {/* Current Version */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">System Version</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-400">Version</div>
            <div className="text-lg font-bold">1.0.0</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Build Date</div>
            <div className="text-lg">{new Date().toLocaleDateString()}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Run ID</div>
            <div className="text-lg">{agentMemory?.run_id || 'N/A'}</div>
          </div>
        </div>
      </div>

      {/* Detected Issues */}
      {issues.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Detected Issues</h3>
          <div className="space-y-2">
            {issues.map((issue, idx) => (
              <div key={idx} className={`p-3 rounded ${issue.severity === 'critical' ? 'bg-red-900' : issue.severity === 'high' ? 'bg-yellow-900' : 'bg-gray-700'}`}>
                <div className="font-bold">{issue.type}</div>
                <div className="text-sm text-gray-300">{issue.message}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upgrade Plan */}
      {upgradePlan && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Pending Upgrade Plan</h3>
          <div className="space-y-4">
            <div>
              <div className="text-sm text-gray-400">Plan ID</div>
              <div className="font-mono">{upgradePlan.plan_id}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Status</div>
              <div className={`inline-block px-2 py-1 rounded ${upgradePlan.status === 'ready' ? 'bg-green-600' : 'bg-yellow-600'}`}>
                {upgradePlan.status.toUpperCase()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Changes</div>
              <ul className="list-disc list-inside mt-2">
                {upgradePlan.changes?.map((change: any, idx: number) => (
                  <li key={idx} className="text-sm">{change.action}</li>
                ))}
              </ul>
            </div>
            <div>
              <div className="text-sm text-gray-400">Auto-Apply</div>
              <div className={upgradePlan.auto_apply ? 'text-green-400' : 'text-yellow-400'}>
                {upgradePlan.auto_apply ? 'Yes (Safe changes)' : 'No (Requires approval)'}
              </div>
            </div>
            {testResults && (
              <div>
                <div className="text-sm text-gray-400">Test Results</div>
                <div className="mt-2">
                  <div className="text-green-400">Passed: {testResults.passed}</div>
                  <div className="text-red-400">Failed: {testResults.failed}</div>
                </div>
              </div>
            )}
            <div className="flex gap-2 mt-4">
              {upgradePlan.status === 'ready' && (
                <button
                  onClick={handleApplyUpgrade}
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
                >
                  {loading ? 'Applying...' : 'Apply Upgrade'}
                </button>
              )}
              <button
                onClick={handleRollback}
                disabled={loading}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded disabled:opacity-50"
              >
                Rollback
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agent Memory Status */}
      {agentMemory && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Agent Memory Status</h3>
          <div className="space-y-2">
            <div>
              <div className="text-sm text-gray-400">Total Tasks</div>
              <div className="text-lg">{agentMemory.tasks?.length || 0}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Completed</div>
              <div className="text-lg text-green-400">
                {agentMemory.tasks?.filter((t: any) => t.status === 'completed').length || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">In Progress</div>
              <div className="text-lg text-yellow-400">
                {agentMemory.tasks?.filter((t: any) => t.status === 'in_progress').length || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Last Updated</div>
              <div className="text-sm">{agentMemory.last_updated || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {!upgradePlan && issues.length === 0 && (
        <div className="bg-gray-800 p-6 rounded-lg text-center text-gray-400">
          No pending upgrades. System is up to date.
        </div>
      )}
    </div>
  )
}
