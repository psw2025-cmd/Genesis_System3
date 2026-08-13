/**
 * App Self-Test Component
 * Shows system status and verifies all endpoints on app load
 * MUST be visible in UI - no silent failures
 */
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

interface TestResult {
  name: string
  status: 'ok' | 'error' | 'warning'
  message: string
  endpoint?: string
}

export default function AppSelfTest() {
  const [tests, setTests] = useState<TestResult[]>([])
  const [allPassed, setAllPassed] = useState(false)
  const [isRunning, setIsRunning] = useState(true)

  useEffect(() => {
    runSelfTest()
  }, [])

  const runSelfTest = async () => {
    setIsRunning(true)
    const testResults: TestResult[] = []

    // Test 1: Backend Health
    try {
      const res = await axios.get(`${API_BASE}/api/health`, { timeout: 5000 })
      if (res.status === 200) {
        testResults.push({
          name: 'Backend Connection',
          status: 'ok',
          message: 'Backend is running and responding',
          endpoint: '/api/health'
        })
      } else {
        testResults.push({
          name: 'Backend Connection',
          status: 'error',
          message: `Backend returned HTTP ${res.status}`,
          endpoint: '/api/health'
        })
      }
    } catch (error: any) {
      testResults.push({
        name: 'Backend Connection',
        status: 'error',
        message: `Cannot connect to backend: ${error.message}`,
        endpoint: '/api/health'
      })
    }

    // Test 2: Learning System
    try {
      const res = await axios.get(`${API_BASE}/api/learning/status`, { timeout: 5000 })
      if (res.status === 200) {
        testResults.push({
          name: 'Learning System',
          status: 'ok',
          message: res.data.status === 'active' ? 'Learning system active' : 'Learning system available (inactive)',
          endpoint: '/api/learning/status'
        })
      } else {
        testResults.push({
          name: 'Learning System',
          status: 'error',
          message: `HTTP ${res.status}`,
          endpoint: '/api/learning/status'
        })
      }
    } catch (error: any) {
      testResults.push({
        name: 'Learning System',
        status: 'error',
        message: `Error: ${error.message}`,
        endpoint: '/api/learning/status'
      })
    }

    // Test 3: Forensic System
    try {
      const res = await axios.get(`${API_BASE}/api/forensic/report`, { timeout: 5000 })
      if (res.status === 200) {
        testResults.push({
          name: 'Forensic System',
          status: 'ok',
          message: 'Forensic analysis available',
          endpoint: '/api/forensic/report'
        })
      } else {
        testResults.push({
          name: 'Forensic System',
          status: 'error',
          message: `HTTP ${res.status}`,
          endpoint: '/api/forensic/report'
        })
      }
    } catch (error: any) {
      testResults.push({
        name: 'Forensic System',
        status: 'error',
        message: `Error: ${error.message}`,
        endpoint: '/api/forensic/report'
      })
    }

    // Test 4: Validation System
    try {
      const res = await axios.get(`${API_BASE}/api/validation/status`, { timeout: 5000 })
      if (res.status === 200) {
        testResults.push({
          name: 'Validation System',
          status: 'ok',
          message: 'Validation system available',
          endpoint: '/api/validation/status'
        })
      } else {
        testResults.push({
          name: 'Validation System',
          status: 'error',
          message: `HTTP ${res.status}`,
          endpoint: '/api/validation/status'
        })
      }
    } catch (error: any) {
      testResults.push({
        name: 'Validation System',
        status: 'error',
        message: `Error: ${error.message}`,
        endpoint: '/api/validation/status'
      })
    }

    // Test 5: Data Endpoints
    const dataEndpoints = [
      { name: 'Chain Data', path: '/api/chain/NIFTY' },
      { name: 'Signal Data', path: '/api/signal/top' },
      { name: 'Position Data', path: '/api/positions' },
      { name: 'PnL Data', path: '/api/pnl' }
    ]

    for (const ep of dataEndpoints) {
      try {
        const res = await axios.get(`${API_BASE}${ep.path}`, { timeout: 5000 })
        if (res.status === 200) {
          testResults.push({
            name: ep.name,
            status: 'ok',
            message: 'Data available',
            endpoint: ep.path
          })
        } else {
          testResults.push({
            name: ep.name,
            status: 'error',
            message: `HTTP ${res.status}`,
            endpoint: ep.path
          })
        }
      } catch (error: any) {
        testResults.push({
          name: ep.name,
          status: 'error',
          message: `Error: ${error.message}`,
          endpoint: ep.path
        })
      }
    }

    setTests(testResults)
    setAllPassed(testResults.every(t => t.status === 'ok'))
    setIsRunning(false)
  }

  if (isRunning) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          <span className="text-sm">Running system self-test...</span>
        </div>
      </div>
    )
  }

  const errorCount = tests.filter(t => t.status === 'error').length
  const warningCount = tests.filter(t => t.status === 'warning').length

  return (
    <div className={`border rounded-lg p-4 mb-4 ${
      allPassed 
        ? 'bg-green-900 border-green-700' 
        : errorCount > 0 
          ? 'bg-red-900 border-red-700' 
          : 'bg-yellow-900 border-yellow-700'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold">
          System Self-Test
          {allPassed && ' ✅'}
          {errorCount > 0 && ` ❌ (${errorCount} errors)`}
          {warningCount > 0 && !allPassed && ` ⚠️ (${warningCount} warnings)`}
        </h3>
        <button
          onClick={runSelfTest}
          className="px-3 py-1 bg-blue-600 rounded text-sm hover:bg-blue-700"
        >
          Re-test
        </button>
      </div>
      
      <div className="space-y-2">
        {tests.map((test, idx) => (
          <div key={idx} className="flex items-center gap-2 text-sm">
            <span>
              {test.status === 'ok' && '✅'}
              {test.status === 'error' && '❌'}
              {test.status === 'warning' && '⚠️'}
            </span>
            <span className="font-medium">{test.name}:</span>
            <span className={test.status === 'error' ? 'text-red-300' : 'text-gray-300'}>
              {test.message}
            </span>
          </div>
        ))}
      </div>

      {errorCount > 0 && (
        <div className="mt-3 p-2 bg-red-800 rounded text-sm">
          <strong>⚠️ Critical:</strong> {errorCount} system(s) failed. Some features may not work.
        </div>
      )}
    </div>
  )
}
