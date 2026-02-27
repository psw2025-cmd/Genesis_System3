/**
 * EmptyState Component
 * Shows explicit empty state UI when no data is available
 */
import React from 'react'

interface EmptyStateProps {
  title?: string
  reason?: string
  lastUpdated?: string | null
  actions?: React.ReactNode
  icon?: string
}

export default function EmptyState({
  title = "No data yet",
  reason,
  lastUpdated,
  actions,
  icon = "📊"
}: EmptyStateProps) {
  return (
    <div className="p-6 bg-gray-800 border border-gray-700 rounded-lg">
      <div className="text-center">
        <div className="text-4xl mb-4">{icon}</div>
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        {reason && (
          <p className="text-gray-300 mb-4">{reason}</p>
        )}
        {lastUpdated && (
          <p className="text-sm text-gray-400 mb-4">
            Last updated: {new Date(lastUpdated).toLocaleString()}
          </p>
        )}
        {actions && (
          <div className="mt-4">
            {actions}
          </div>
        )}
      </div>
    </div>
  )
}
