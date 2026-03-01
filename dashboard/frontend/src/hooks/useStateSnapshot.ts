/**
 * useStateSnapshot - SSOT state hook
 * Fetches unified state from /api/state and exposes snapshot + version.
 * Use for consistent state across all dashboard pages.
 */
import { useState, useEffect, useCallback } from 'react'
import { API_BASE } from '../config'

export interface StateSnapshot {
  state_version: number
  timestamp_utc?: string
  timestamp_ist?: string
  mode: string
  data_source?: string
  broker?: { connected: boolean; status?: string }
  market?: { is_open: boolean; reason?: string }
  qc?: { status: string; failures?: string[] }
  signals?: Record<string, unknown>
  positions?: unknown[]
  pnl?: { unrealized?: number; realized?: number; total?: number }
  risk?: Record<string, unknown>
  [key: string]: unknown
}

interface UseStateSnapshotOptions {
  pollInterval?: number // ms, 0 = no polling
  enabled?: boolean
}

export function useStateSnapshot(options: UseStateSnapshotOptions = {}) {
  const { pollInterval = 3000, enabled = true } = options
  const [snapshot, setSnapshot] = useState<StateSnapshot | null>(null)
  const [version, setVersion] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchState = useCallback(async () => {
    if (!enabled) return
    try {
      const res = await fetch(`${API_BASE}/api/state`)
      if (!res.ok) throw new Error(`State API ${res.status}`)
      const data: StateSnapshot = await res.json()
      setSnapshot(data)
      setVersion(data.state_version ?? 0)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch state')
      setSnapshot(null)
    } finally {
      setLoading(false)
    }
  }, [enabled])

  useEffect(() => {
    fetchState()
  }, [fetchState])

  useEffect(() => {
    if (!enabled || pollInterval <= 0) return
    const id = setInterval(fetchState, pollInterval)
    return () => clearInterval(id)
  }, [enabled, pollInterval, fetchState])

  return {
    snapshot,
    version,
    loading,
    error,
    refresh: fetchState,
  }
}
