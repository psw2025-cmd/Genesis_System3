/**
 * ErrorBanner Component
 * Shows explicit error UI when API calls fail
 */
import React from 'react'

interface ErrorBannerProps {
  endpoint: string
  status?: number | null
  message: string
  onRetry?: () => void
}

export default function ErrorBanner({
  endpoint,
  status,
  message,
  onRetry
}: ErrorBannerProps) {
  return (
    <div className="p-4 bg-red-900 border border-red-700 rounded-lg mb-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">❌</span>
            <h3 className="text-lg font-bold text-red-200">Error Loading Data</h3>
          </div>
          <div className="text-sm text-red-300 space-y-1">
            <div>
              <strong>Endpoint:</strong> <code className="bg-red-800 px-1 rounded">{endpoint}</code>
            </div>
            {status && (
              <div>
                <strong>HTTP Status:</strong> <span className="font-mono">{status}</span>
              </div>
            )}
            <div>
              <strong>Error:</strong> {message}
            </div>
          </div>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-4 px-4 py-2 bg-red-700 hover:bg-red-600 rounded text-sm font-medium"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  )
}
