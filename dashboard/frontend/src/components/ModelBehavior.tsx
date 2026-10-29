import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

export default function ModelBehavior() {
  const [logs, setLogs] = useState<string[]>([])
  const [secrets, setSecrets] = useState<any>(null)
  const [qc, setQc] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [logsRes, secretsRes, qcRes] = await Promise.allSettled([
          axios.get(`${API_BASE}/api/logs/tail?lines=200`, { timeout: 5000 }),
          axios.get(`${API_BASE}/api/audit/secrets`, { timeout: 5000 }),
          axios.get(`${API_BASE}/api/qc`, { timeout: 5000 })
        ])
        
        if (logsRes.status === 'fulfilled') {
          setLogs(logsRes.value.data.logs || [])
        } else {
          console.warn('Logs fetch failed:', logsRes.reason?.message)
          setLogs([])
        }
        
        if (secretsRes.status === 'fulfilled') {
          setSecrets(secretsRes.value.data)
        } else {
          console.warn('Secrets fetch failed:', secretsRes.reason?.message)
          setSecrets({ secrets_found: 0, status: 'UNKNOWN' })
        }
        
        if (qcRes.status === 'fulfilled') {
          const qcData = qcRes.value.data
          // Ensure qc_passed field exists
          if (qcData && !('qc_passed' in qcData)) {
            qcData.qc_passed = qcData.status === 'PASS'
            qcData.total_contracts = qcData.total_contracts || 0
            qcData.underlying_count = qcData.underlying_count || 0
          }
          setQc(qcData)
        } else {
          console.warn('QC fetch failed:', qcRes.reason?.message)
          setQc({ qc_passed: false, total_contracts: 0, underlying_count: 0, status: 'UNKNOWN' })
        }
      } catch (error) {
        console.error('Error fetching model data:', error)
        // Set defaults on error
        setLogs([])
        setSecrets({ secrets_found: 0, status: 'UNKNOWN' })
        setQc({ qc_passed: false, total_contracts: 0, underlying_count: 0, status: 'UNKNOWN' })
      }
    }
    fetchData()
    // Optimized polling: 5000ms (5 seconds) - already optimal
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Model & System Behavior</h2>

      {/* Model Status */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Model Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-400">Model Used</div>
            <div className="text-lg">Ensemble / Fallback</div>
            <div className="text-xs text-gray-500">Check logs for details</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Fallback Counters</div>
            <div className="text-lg">See logs</div>
          </div>
        </div>
      </div>

      {/* Data Quality */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Data Quality</h3>
        {qc && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-400">Total Contracts</div>
              <div className="text-2xl font-bold">{qc.total_contracts || 0}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Underlying Count</div>
              <div className="text-2xl font-bold">{qc.underlying_count || 0}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">QC Status</div>
              <div className={`text-2xl font-bold ${qc.qc_passed ? 'text-green-400' : 'text-red-400'}`}>
                {qc.qc_passed ? 'PASS' : 'FAIL'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Secrets Scan */}
      <div className={`p-6 rounded-lg ${secrets?.secrets_found === 0 ? 'bg-green-900' : 'bg-red-900'}`}>
        <h3 className="text-xl font-bold mb-4">Security Audit</h3>
        <div className="space-y-2">
          <div className="text-2xl font-bold">
            Secrets Found: {secrets?.secrets_found || 0}
          </div>
          <div className={`text-lg ${secrets?.status === 'PASS' ? 'text-green-400' : 'text-red-400'}`}>
            Status: {secrets?.status || 'UNKNOWN'}
          </div>
          {secrets?.scanned_files && secrets.scanned_files.length > 0 && (
            <div>
              <div className="text-sm text-gray-300">Files with secrets:</div>
              <ul className="list-disc list-inside">
                {secrets.scanned_files.map((f: any, idx: number) => (
                  <li key={idx}>{f.file}: {f.secrets} secrets</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Logs */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Runtime Logs (Last 200 lines)</h3>
        <div className="bg-black p-4 rounded font-mono text-xs overflow-auto max-h-96">
          {logs.length > 0 ? (
            logs.map((line, idx) => (
              <div key={idx} className="text-green-400">{line}</div>
            ))
          ) : (
            <div className="text-gray-400">No logs available</div>
          )}
        </div>
      </div>
    </div>
  )
}
