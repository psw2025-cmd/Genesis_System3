import { useState } from 'react'
import { API_BASE } from '../config'

export function AuthUnlock({ compact = false }: { compact?: boolean }) {
  const [apiKey, setApiKey] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  async function unlock() {
    if (!apiKey.trim()) {
      setMessage('Enter the dashboard API key to unlock read-only broker data.')
      return
    }
    setBusy(true)
    setMessage('')
    try {
      const r = await fetch(`${API_BASE || window.location.origin}/api/auth/session`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ api_key: apiKey.trim() }),
      })
      if (!r.ok) throw new Error(r.status === 401 ? 'Invalid dashboard API key' : `Auth failed (${r.status})`)
      setMessage('Unlocked. Refreshing read-only data...')
      window.setTimeout(() => window.location.reload(), 500)
    } catch (err: any) {
      setMessage(err?.message || 'Unable to unlock dashboard')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className={compact ? 'space-y-2' : 'card p-4 border border-amber/30 bg-amber/5 space-y-3'}>
      {!compact && (
        <div>
          <div className="text-xs text-text-muted uppercase tracking-wider">Read-only broker unlock</div>
          <div className="text-sm text-text-primary font-semibold">Broker funds, holdings, and positions require dashboard API auth.</div>
        </div>
      )}
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') unlock() }}
          placeholder="Dashboard API key"
          className="bg-surface-2 border border-border rounded px-3 py-2 text-sm text-text-primary flex-1"
          autoComplete="current-password"
        />
        <button
          onClick={unlock}
          disabled={busy}
          className="px-3 py-2 rounded bg-accent text-white text-sm font-semibold disabled:opacity-50"
        >
          {busy ? 'Unlocking...' : 'Unlock'}
        </button>
      </div>
      {message && <div className="text-xs text-amber">{message}</div>}
    </div>
  )
}
