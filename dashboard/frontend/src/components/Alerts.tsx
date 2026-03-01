import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        // Try SSOT first for alerts
        const stateRes = await axios.get(`${API_BASE}/api/state`).catch(() => null)
        if (stateRes && stateRes.data && stateRes.data.alerts) {
          const ssotAlerts = stateRes.data.alerts || []
          setAlerts(ssotAlerts)
          setUnreadCount(ssotAlerts.filter((a: any) => !(a.read ?? false)).length)
        } else {
          // Fallback to alerts endpoints
          const [recentRes, unreadRes] = await Promise.all([
            axios.get(`${API_BASE}/api/alerts/recent?limit=50`),
            axios.get(`${API_BASE}/api/alerts/unread`)
          ])
          setAlerts(recentRes.data.alerts || [])
          setUnreadCount(unreadRes.data.count || 0)
        }
      } catch (error) {
        console.error('Error fetching alerts:', error)
        // Fallback to alerts endpoints
        try {
          const [recentRes, unreadRes] = await Promise.all([
            axios.get(`${API_BASE}/api/alerts/recent?limit=50`),
            axios.get(`${API_BASE}/api/alerts/unread`)
          ])
          setAlerts(recentRes.data.alerts || [])
          setUnreadCount(unreadRes.data.count || 0)
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError)
        }
      }
    }

    fetchAlerts()
    // Optimized polling: 5000ms (5 seconds) - already optimal
    const interval = setInterval(fetchAlerts, 5000)
    return () => clearInterval(interval)
  }, [])

  const getSeverityColor = (severity: string) => {
    const s = (severity || '').toLowerCase()
    switch (s) {
      case 'critical': return 'bg-red-600'
      case 'error': return 'bg-red-500'
      case 'warn':
      case 'warning': return 'bg-yellow-500'
      case 'info': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  const getTypeIcon = (type: string) => {
    const t = (type || '').toLowerCase()
    if (t.includes('price')) return '💰'
    if (t.includes('position')) return '📊'
    if (t.includes('system') || t.includes('broker')) return '⚙️'
    if (t.includes('pnl')) return '💵'
    if (t.includes('risk')) return '⚠️'
    return '📢'
  }

  // Normalize alert format (SSOT uses level/code/ts; legacy uses severity/type/title/timestamp)
  const normalizeAlert = (a: any) => ({
    id: a.id || a.code || a.ts,
    severity: a.severity || a.level || 'info',
    type: a.type || a.code || 'system_alert',
    title: a.title || a.code || (a.level ? `${a.level} Alert` : 'Alert'),
    message: a.message || '',
    timestamp: a.timestamp || a.ts,
    read: a.read ?? false
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Alerts & Notifications</h2>
        {unreadCount > 0 && (
          <span className="px-3 py-1 bg-red-500 rounded-full text-sm">
            {unreadCount} Unread
          </span>
        )}
      </div>

      {alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert, idx) => {
            const a = normalizeAlert(alert)
            return (
            <div
              key={a.id || idx}
              className={`bg-gray-800 p-4 rounded-lg border-l-4 ${
                getSeverityColor(a.severity)
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getTypeIcon(a.type)}</span>
                    <h3 className="text-lg font-bold">{a.title}</h3>
                    <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(a.severity)}`}>
                      {(a.severity || 'UNKNOWN').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-300 mb-2">{a.message}</p>
                  <div className="text-xs text-gray-400">
                    {a.timestamp ? new Date(a.timestamp).toLocaleString() : ''}
                  </div>
                </div>
                {!a.read && (
                  <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                )}
              </div>
            </div>
          )})}
        </div>
      ) : (
        <div className="text-gray-400 text-center py-12">
          No alerts at this time
        </div>
      )}
    </div>
  )
}
