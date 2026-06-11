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

function asArray(value: any): any[] {
  return Array.isArray(value) ? value : []
}

function safeText(value: any, fallback = 'N/A'): string {
  if (value === null || value === undefined || value === '') return fallback
  return String(value)
}

export default function AgentConsole() {
  const [agentMemory, setAgentMemory] = useState<any>(null)
  const [upgradePlan, setUpgradePlan] = useState<any>(null)
  const [testResults, setTestResults] = useState<any>(null)
  const [issues, setIssues] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [lastError, setLastError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const fetchAgentData = async () => {
      try {
        setLastError(null)

        // Try Electron API first, then HTTP API.
        if (window.electronAPI) {
          const memory = await window.electronAPI.getAgentMemory()
          if (!cancelled) setAgentMemory(memory || {})
        } else {
          const res = await axios.get(`${API_BASE}/api/agent/memory`, { timeout: 8000 })
          if (!cancelled) setAgentMemory(res.data || {})
        }

        // Fetch upgrade plan. API shape may vary, so render defensively.
        let planData: any = null
        try {
          const planRes = await axios.get(`${API_BASE}/api/agent/upgrade-plan`, { timeout: 8000 })
          planData = planRes.data || null
          const status = safeText(planData?.status, 'none').toLowerCase()
          if (!cancelled) setUpgradePlan(planData && status !== 'none' ? planData : null)
        } catch (error: any) {
          if (!cancelled) setUpgradePlan(null)
        }

        // Fetch issues. Always store an array.
        try {
          const issuesRes = await axios.get(`${API_BASE}/api/agent/issues`, { timeout: 8000 })
          if (!cancelled) setIssues(asArray(issuesRes.data?.issues))
        } catch (error: any) {
          console.warn('Error fetching issues:', error)
          if (!cancelled) setIssues([])
        }

        // Fetch test results only when a plan id exists.
        const planId = planData?.plan_id
        if (planId) {
          try {
            const testRes = await axios.get(`${API_BASE}/api/agent/test-results/${encodeURIComponent(planId)}`, { timeout: 8000 })
            if (!cancelled) setTestResults(testRes.data || null)
          } catch (error: any) {
            if (!cancelled) setTestResults(null)
          }
        } else if (!cancelled) {
          setTestResults(null)
        }
      } catch (error: any) {
        console.error('Error fetching agent data:', error)
        if (!cancelled) {
          setLastError(error?.message || 'Agent data fetch failed')
          setAgentMemory((prev: any) => prev || {})
          setIssues([])
          setUpgradePlan(null)
          setTestResults(null)
        }
      }
    }

    fetchAgentData()
    const interval = setInterval(fetchAgentData, 10000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  const handleApplyUpgrade = async () => {
    if (!upgradePlan?.plan_id) return

    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/agent/apply-upgrade`, {
        plan_id: upgradePlan.plan_id,
      })

      if (res.data?.success) {
        alert('Upgrade applied successfully!')
        setUpgradePlan(null)

        if (window.electronAPI) {
          await window.electronAPI.showNotification({
            title: 'Upgrade Applied',
            body: 'System upgrade has been applied successfully',
          })
        }
      } else {
        alert(`Upgrade failed: ${safeText(res.data?.message, 'Unknown error')}`)
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
      if (res.data?.success) {
        alert('Rollback successful!')
      } else {
        alert(`Rollback failed: ${safeText(res.data?.message, 'Unknown error')}`)
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
        if (result?.success) {
          window.open(`${API_BASE}/api/proof-pack`, '_blank')
        }
      } else {
        window.open(`${API_BASE}/api/proof-pack`, '_blank')
      }
    } catch (error: any) {
      alert(`Error downloading proof pack: ${error.message}`)
    }
  }

  const handlePauseAgent = async () => {
    try {
      const res = await axios.post(`${API_BASE}/api/agent/pause`)
      alert(res.data?.paused ? 'Agent paused' : 'Agent resumed')
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const memoryTasks = asArray(agentMemory?.tasks)
  const completedCount = memoryTasks.filter((t: any) => t?.status === 'completed').length
  const inProgressCount = memoryTasks.filter((t: any) => t?.status === 'in_progress').length
  const planStatus = safeText(upgradePlan?.status, 'unknown')
  const planChanges = asArray(upgradePlan?.changes)

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

      {lastError && (
        <div className="bg-yellow-900 border border-yellow-700 p-4 rounded-lg text-yellow-100">
          Agent API warning: {lastError}. Showing safe fallback values.
        </div>
      )}

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
            <div className="text-lg">{safeText(agentMemory?.run_id)}</div>
          </div>
        </div>
      </div>

      {/* Detected Issues */}
      {issues.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Detected Issues</h3>
          <div className="space-y-2">
            {issues.map((issue, idx) => {
              const severity = safeText(issue?.severity, 'normal').toLowerCase()
              return (
                <div key={idx} className={`p-3 rounded ${severity === 'critical' ? 'bg-red-900' : severity === 'high' ? 'bg-yellow-900' : 'bg-gray-700'}`}>
                  <div className="font-bold">{safeText(issue?.type, 'Issue')}</div>
                  <div className="text-sm text-gray-300">{safeText(issue?.message, 'No details')}</div>
                </div>
              )
            })}
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
              <div className="font-mono">{safeText(upgradePlan.plan_id)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Status</div>
              <div className={`inline-block px-2 py-1 rounded ${planStatus.toLowerCase() === 'ready' ? 'bg-green-600' : 'bg-yellow-600'}`}>
                {planStatus.toUpperCase()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Changes</div>
              {planChanges.length > 0 ? (
                <ul className="list-disc list-inside mt-2">
                  {planChanges.map((change: any, idx: number) => (
                    <li key={idx} className="text-sm">{safeText(change?.action || change, 'Change')}</li>
                  ))}
                </ul>
              ) : (
                <div className="text-sm text-gray-400 mt-2">No change list provided</div>
              )}
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
                  <div className="text-green-400">Passed: {safeText(testResults.passed, '0')}</div>
                  <div className="text-red-400">Failed: {safeText(testResults.failed, '0')}</div>
                </div>
              </div>
            )}
            <div className="flex gap-2 mt-4">
              {planStatus.toLowerCase() === 'ready' && (
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
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Agent Memory Status</h3>
        <div className="space-y-2">
          <div>
            <div className="text-sm text-gray-400">Total Tasks</div>
            <div className="text-lg">{memoryTasks.length}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Completed</div>
            <div className="text-lg text-green-400">{completedCount}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">In Progress</div>
            <div className="text-lg text-yellow-400">{inProgressCount}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Last Updated</div>
            <div className="text-sm">{safeText(agentMemory?.last_updated)}</div>
          </div>
        </div>
      </div>

      {!upgradePlan && issues.length === 0 && (
        <div className="bg-gray-800 p-6 rounded-lg text-center text-gray-400">
          No pending upgrades. System is up to date.
        </div>
      )}
    </div>
  )
}
