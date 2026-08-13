import React, { useState, useEffect } from 'react'
import { API_BASE } from '../config'
import axios from 'axios'

interface BackendConnectivityBannerProps {
  onRetry?: () => void
}

export default function BackendConnectivityBanner({ onRetry }: BackendConnectivityBannerProps) {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [retryCount, setRetryCount] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const checkBackend = async (attempt = 0) => {
    try {
      const response = await axios.get(`${API_BASE}/api/health`, { timeout: 2000 })
      if (response.status === 200) {
        setStatus('connected')
        setError(null)
        return true
      }
    } catch (err: any) {
      setError(err.message || 'Connection failed')
      if (attempt < 5) {
        // Exponential backoff: 1s, 2s, 4s, 8s, 16s
        const delay = Math.pow(2, attempt) * 1000
        setTimeout(() => checkBackend(attempt + 1), delay)
        setRetryCount(attempt + 1)
      } else {
        setStatus('disconnected')
      }
      return false
    }
    return false
  }

  useEffect(() => {
    checkBackend()
    // Re-check every 10 seconds
    const interval = setInterval(() => {
      if (status !== 'connected') {
        checkBackend(0)
      }
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  if (status === 'connected') {
    return null // Don't show banner when connected
  }

  return (
    <div className="bg-red-900/20 border border-red-700 p-4 rounded-lg mb-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-bold text-red-400 mb-1">
            {status === 'checking' ? 'Checking backend connection...' : 'Backend not running'}
          </div>
          {error && (
            <div className="text-sm text-red-300 mb-2">
              {error}
              {retryCount > 0 && ` (Retry ${retryCount}/5)`}
            </div>
          )}
          <div className="text-sm text-gray-400">
            The backend server is required for the dashboard to function. 
            {status === 'disconnected' && ' Please start the backend or check your connection.'}
          </div>
        </div>
        {(status === 'disconnected' || retryCount > 0) && (
          <button
            onClick={() => {
              setStatus('checking')
              setRetryCount(0)
              setError(null)
              checkBackend(0)
              if (onRetry) onRetry()
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white text-sm font-semibold"
          >
            Retry Connection
          </button>
        )}
      </div>
    </div>
  )
}
