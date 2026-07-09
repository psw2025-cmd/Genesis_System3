import { useEffect, useMemo, useState } from 'react'

type Probe = {
  endpoint: string
  ok: boolean
  status: number
  json?: any
  error?: string
}

const CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

const CORE_ENDPOINTS = [
  '/api/health',
  '/api/state',
  '/api/broker/dhan/status',
  '/api/broker/funds',
  '/api/broker/holdings',
  '/api/broker/positions/live',
  '/api/gain_rank',
  '/api/pnl',
  '/api/auto_gates',
]

function badge(ok: boolean, label?: string) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '3px 8px', borderRadius: 999,
      fontSize: 11, fontWeight: 800,
      background: ok ? 'rgba(16,185,129,.14)' : 'rgba(239,68,68,.14)',
      color: ok ? 'var(--up)' : 'var(--down)',
      border: `1px solid ${ok ? 'rgba(16,185,129,.35)' : 'rgba(239,68,68,.35)'}`,
    }}>{ok ? 'PASS' : 'BLOCKED'}{label ? ` · ${label}` : ''}</span>
  )
}

function isDhanChain(json: any) {
  if (!json || typeof json !== 'object') return false
  const source = String(json.data_source || json.source || '').toLowerCase()
  const priority = String(json.source_priority || '').toLowerCase()
  const status = String(json.status || '').toUpperCase()
  const combined = `${source} ${priority} ${status}`
  if (json.stale === true) return false
  if (/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock|stale)/i.test(combined)) return false
  const contracts = Array.isArray(json.contracts) ? json.contracts.length : 0
  const spot = Number(json.spot || 0)
  return source === 'dhan' && contracts > 0 && spot > 0
}

function blockedReason(json: any) {
  if (!json || typeof json !== 'object') return 'NO_RESPONSE'
  return json.blocked_reason || json.message || json.status || json.error || 'UNKNOWN'
}

export function EndToEndProof() {
  const [probes, setProbes] = useState<Probe[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRun, setLastRun] = useState<string>('')

  async function runProof() {
    setLoading(true)
    const endpoints = [...CORE_ENDPOINTS, ...CHAIN_SYMBOLS.map(s => `/api/chain/${s}`)]
    const results: Probe[] = []
    for (const endpoint of endpoints) {
      try {
        const r = await fetch(endpoint, { credentials: 'include' })
        const text = await r.text()
        let json: any = null
        try { json = JSON.parse(text) } catch { json = { raw: text.slice(0, 5000) } }
        results.push({ endpoint, ok: r.ok, status: r.status, json })
      } catch (err: any) {
        results.push({ endpoint, ok: false, status: 0, error: String(err) })
      }
    }
    setProbes(results)
    setLastRun(new Date().toLocaleString())
    setLoading(false)
  }

  useEffect(() => { runProof() }, [])

  const chains = useMemo(() => probes.filter(p => p.endpoint.startsWith('/api/chain/')), [probes])
  const core = useMemo(() => probes.filter(p => !p.endpoint.startsWith('/api/chain/')), [probes])
  const chainPass = chains.length === CHAIN_SYMBOLS.length && chains.every(p => p.ok && isDhanChain(p.json))
  const corePass = core.length > 0 && core.every(p => p.ok)
  const fakeBlocked = chains.every(p => !String(p.json?.data_source || '').includes('csv_fallback'))
  const overall = corePass && chainPass && fakeBlocked

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>End-to-End Visual Truth Proof</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
            Dhan-only data truth, paper/analyzer proof, no CSV/stale/synthetic display as live.
          </div>
        </div>
        <button onClick={runProof} disabled={loading} style={{
          padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)',
          background: 'var(--surface-2)', color: 'var(--text-primary)', cursor: 'pointer'
        }}>{loading ? 'Checking...' : 'Recheck Now'}</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(160px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card">{badge(overall, 'FULL E2E')}<div style={{ marginTop: 8, fontSize: 12 }}>Overall visual proof</div></div>
        <div className="card">{badge(corePass, 'API')}<div style={{ marginTop: 8, fontSize: 12 }}>Core endpoints</div></div>
        <div className="card">{badge(chainPass, 'DHAN CHAIN')}<div style={{ marginTop: 8, fontSize: 12 }}>Real Dhan option chain</div></div>
        <div className="card">{badge(fakeBlocked, 'NO FAKE')}<div style={{ marginTop: 8, fontSize: 12 }}>No csv/stale/synthetic as live</div></div>
      </div>

      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 14 }}>
        Last run: {lastRun || 'not yet'} · Live trading remains outside this visual proof.
      </div>

      <h3 style={{ fontSize: 16 }}>Dhan Option Chain Proof</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, marginBottom: 18 }}>
        <thead><tr>
          <th className="thead">Symbol</th><th className="thead">Visual Status</th><th className="thead">Source</th><th className="thead">Priority</th><th className="thead">Status</th><th className="thead">Spot</th><th className="thead">Contracts</th><th className="thead">Reason</th>
        </tr></thead>
        <tbody>
          {chains.map(p => {
            const ok = p.ok && isDhanChain(p.json)
            const sym = p.endpoint.split('/').pop()
            return <tr key={p.endpoint}>
              <td className="tcell"><b>{sym}</b></td>
              <td className="tcell">{badge(ok)}</td>
              <td className="tcell">{String(p.json?.data_source || p.json?.source || '-')}</td>
              <td className="tcell">{String(p.json?.source_priority || '-')}</td>
              <td className="tcell">{String(p.json?.status || p.status)}</td>
              <td className="tcell">{String(p.json?.spot ?? '-')}</td>
              <td className="tcell">{String(p.json?.total_contracts ?? (Array.isArray(p.json?.contracts) ? p.json.contracts.length : '-'))}</td>
              <td className="tcell" style={{ color: ok ? 'var(--text-muted)' : 'var(--down)' }}>{ok ? 'REAL_DHAN_VISIBLE' : blockedReason(p.json)}</td>
            </tr>
          })}
        </tbody>
      </table>

      <h3 style={{ fontSize: 16 }}>Core API / Dashboard Data Proof</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead><tr><th className="thead">Endpoint</th><th className="thead">HTTP</th><th className="thead">Visual Status</th><th className="thead">Important Status</th></tr></thead>
        <tbody>
          {core.map(p => <tr key={p.endpoint}>
            <td className="tcell"><code>{p.endpoint}</code></td>
            <td className="tcell">{p.status}</td>
            <td className="tcell">{badge(p.ok)}</td>
            <td className="tcell">{String(p.json?.status || p.json?.broker_status || p.json?.mode || p.error || '-')}</td>
          </tr>)}
        </tbody>
      </table>
    </div>
  )
}
