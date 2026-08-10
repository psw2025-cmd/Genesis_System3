import { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'
import { cn } from '../lib/utils'

interface TokenHealth {
  health: string
  token?: { hours_remaining?: number; expired?: boolean; secret_version?: string; rotation_schedule?: string; reload_count?: number }
  connection_stability?: { state?: string; uptime_pct_1h?: number | null; consecutive_failures?: number; flap_count?: number }
  policy?: { single_writer?: string; rotation_schedule?: string; validate_before_persist?: boolean }
}

function Row({ label, value, ok }: { label: string; value: string; ok?: boolean }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-sm text-text-muted">{label}</span>
      <span className={cn('num text-sm font-mono font-medium',
        ok === true ? 'text-up' : ok === false ? 'text-down' : 'text-text-primary'
      )}>{value}</span>
    </div>
  )
}

export function TokenHealthCard() {
  const [th, setTh] = useState<TokenHealth | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/broker/token-health`, { headers: API_HEADERS, timeout: 15000 })
        if (alive) { setTh(res.data?.data ?? res.data); setErr(null) }
      } catch (e: any) {
        if (alive) setErr(e?.message || 'failed')
      }
    }
    load()
    const t = setInterval(load, 60000)
    return () => { alive = false; clearInterval(t) }
  }, [])

  const tok = th?.token || {}
  const stab = th?.connection_stability || {}
  const healthy = th?.health === 'HEALTHY'

  return (
    <div className="card p-5" data-testid="token-health-card">
      <h3 className="text-sm font-semibold text-text-primary mb-3">Dhan Token Rotation Health</h3>
      {err && <Row label="Status" value={`UNAVAILABLE (${err})`} ok={false} />}
      {th && (<>
        <Row label="Health" value={th.health || '--'} ok={healthy ? true : th.health === 'EXPIRED' ? false : undefined} />
        <Row label="Token Expires In" value={tok.hours_remaining != null ? `${tok.hours_remaining}h` : '--'} ok={tok.expired === true ? false : tok.hours_remaining != null ? tok.hours_remaining > 3 : undefined} />
        <Row label="Secret Version" value={tok.secret_version ?? '--'} />
        <Row label="Rotation Schedule" value={th.policy?.rotation_schedule ?? tok.rotation_schedule ?? '--'} />
        <Row label="Single Writer" value={th.policy?.single_writer ? 'ROTATION JOB ONLY' : '--'} ok={Boolean(th.policy?.single_writer)} />
        <Row label="Validate Before Persist" value={String(th.policy?.validate_before_persist ?? '--')} ok={th.policy?.validate_before_persist === true} />
        <Row label="Connection State" value={stab.state ?? '--'} ok={stab.state === 'CONNECTED' ? true : stab.state?.startsWith('DOWN') ? false : undefined} />
        <Row label="Uptime (1h)" value={stab.uptime_pct_1h != null ? `${stab.uptime_pct_1h}%` : '--'} />
      </>)}
    </div>
  )
}
