import { useEffect, useMemo, useState } from 'react'

type Probe = {
  endpoint: string
  ok: boolean
  status: number
  json?: any
  error?: string
}

const CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']
const PROBE_TIMEOUT_MS = 3500
const PROBE_CONCURRENCY = 3
const RATE_LIMIT_RETRY_MS = 1200

const CORE_ENDPOINTS = [
  '/api/health',
  '/api/state',
  '/api/broker/dhan/status',
  '/api/broker/funds',
  '/api/broker/holdings',
  '/api/broker/positions/live',
  '/api/gain_rank',
  '/api/pnl',
  '/api/trades/today',
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
  const contracts = Array.isArray(json.contracts) ? json.contracts.length : Number(json.total_contracts || 0)
  const spot = Number(json.spot || 0)
  return source === 'dhan' && contracts > 0 && spot > 0
}

function blockedReason(json: any) {
  if (!json || typeof json !== 'object') return 'NO_RESPONSE'
  return json.blocked_reason || json.message || json.status || json.error || 'UNKNOWN'
}

function endpoint(probes: Probe[], name: string) {
  return probes.find(p => p.endpoint === name)
}

function hasRows(json: any, ...keys: string[]) {
  if (!json || typeof json !== 'object') return false
  for (const k of keys) {
    if (Array.isArray(json[k])) return true
    if (Array.isArray(json?.data?.[k])) return true
    if (Array.isArray(json?.normalized?.[k])) return true
  }
  return false
}

function isBrokerConnected(json: any) {
  if (!json || typeof json !== 'object') return false
  return json.connected === true || json.success === true || String(json.status || '').toLowerCase().includes('connected')
}

function isLiveTradingBlocked(stateJson: any, brokerJson: any) {
  const raw = stateJson?.live_trading_enabled ?? stateJson?.liveTradingEnabled ?? stateJson?.live_allowed ?? brokerJson?.live_trading_enabled ?? brokerJson?.liveTradingEnabled ?? brokerJson?.live_allowed ?? '0'
  return !(raw === true || String(raw) === '1')
}

function wait(ms: number) {
  return new Promise(resolve => window.setTimeout(resolve, ms))
}

async function probeReadOnlyEndpoint(endpoint: string, allowRateLimitRetry = true): Promise<Probe> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS)
  try {
    const response = await fetch(endpoint, {
      credentials: 'include',
      signal: controller.signal,
      cache: 'no-store',
    })
    const text = await response.text()
    let json: any = null
    try { json = JSON.parse(text) } catch { json = { parse_error: true } }

    if (response.status === 429 && allowRateLimitRetry) {
      const retryAfterSeconds = Number(response.headers.get('retry-after') || 0)
      const retryDelay = retryAfterSeconds > 0
        ? Math.min(retryAfterSeconds * 1000, 3000)
        : RATE_LIMIT_RETRY_MS
      await wait(retryDelay)
      return probeReadOnlyEndpoint(endpoint, false)
    }

    return { endpoint, ok: response.ok, status: response.status, json }
  } catch (err: any) {
    const timedOut = err?.name === 'AbortError'
    return {
      endpoint,
      ok: false,
      status: 0,
      error: timedOut ? `READ_ONLY_PROBE_TIMEOUT_${PROBE_TIMEOUT_MS}MS` : String(err?.name || 'FETCH_ERROR'),
    }
  } finally {
    window.clearTimeout(timeout)
  }
}

async function probeWithBoundedConcurrency(endpoints: string[]): Promise<Probe[]> {
  const results = new Array<Probe>(endpoints.length)
  let nextIndex = 0

  async function worker() {
    while (true) {
      const index = nextIndex
      nextIndex += 1
      if (index >= endpoints.length) return
      results[index] = await probeReadOnlyEndpoint(endpoints[index])
    }
  }

  const workerCount = Math.min(PROBE_CONCURRENCY, endpoints.length)
  await Promise.all(Array.from({ length: workerCount }, () => worker()))
  return results
}

export function EndToEndProof() {
  const [probes, setProbes] = useState<Probe[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRun, setLastRun] = useState<string>('')

  async function runProof() {
    setLoading(true)
    const endpoints = [...CORE_ENDPOINTS, ...CHAIN_SYMBOLS.map(s => `/api/chain/${s}`)]
    const results = await probeWithBoundedConcurrency(endpoints)
    setProbes(results)
    setLastRun(new Date().toLocaleString())
    setLoading(false)
  }

  useEffect(() => { runProof() }, [])

  const chains = useMemo(() => probes.filter(p => p.endpoint.startsWith('/api/chain/')), [probes])
  const core = useMemo(() => probes.filter(p => !p.endpoint.startsWith('/api/chain/')), [probes])
  const chainPass = chains.length === CHAIN_SYMBOLS.length && chains.every(p => p.ok && isDhanChain(p.json))
  const corePass = core.length > 0 && core.every(p => p.ok)
  const noBadSource = chains.every(p => !/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock|stale)/i.test(JSON.stringify(p.json || {})))
  const broker = endpoint(probes, '/api/broker/dhan/status')
  const funds = endpoint(probes, '/api/broker/funds')
  const holdings = endpoint(probes, '/api/broker/holdings')
  const positions = endpoint(probes, '/api/broker/positions/live')
  const state = endpoint(probes, '/api/state')
  const pnl = endpoint(probes, '/api/pnl')
  const trades = endpoint(probes, '/api/trades/today')
  const gates = endpoint(probes, '/api/auto_gates')

  const readiness = [
    { item: 'Dhan broker connection', ok: Boolean(broker?.ok && isBrokerConnected(broker.json)), evidence: broker?.json?.status || broker?.json?.token_status || broker?.status || '-' },
    { item: 'Dhan access token/session', ok: Boolean(broker?.ok && !/invalid|expired|unauthorized|token error/i.test(JSON.stringify(broker.json || {}))), evidence: broker?.json?.token_status || broker?.json?.status || '-' },
    { item: 'Real broker funds/margin', ok: Boolean(funds?.ok && funds.json && !funds.json.blocked && funds.json.success !== false), evidence: funds?.json?.status || funds?.json?.message || funds?.status || funds?.error || '-' },
    { item: 'Real broker holdings response', ok: Boolean(holdings?.ok && holdings.json && holdings.json.success !== false), evidence: hasRows(holdings?.json, 'rows', 'holdings', 'data') ? 'rows visible or empty broker response' : (holdings?.json?.message || holdings?.status || holdings?.error || '-') },
    { item: 'Real broker positions response', ok: Boolean(positions?.ok && positions.json && positions.json.success !== false), evidence: hasRows(positions?.json, 'rows', 'positions', 'data') ? 'rows visible or empty broker response' : (positions?.json?.message || positions?.status || positions?.error || '-') },
    { item: 'Real Dhan option chain for all watched symbols', ok: chainPass, evidence: `${chains.filter(p => p.ok && isDhanChain(p.json)).length}/${CHAIN_SYMBOLS.length}` },
    { item: 'No non-Dhan/stale/fallback markers in chain', ok: noBadSource, evidence: noBadSource ? 'clean' : 'blocked marker found' },
    { item: 'Paper/analyzer P&L endpoint', ok: Boolean(pnl?.ok), evidence: pnl?.json?.status || pnl?.status || pnl?.error || '-' },
    { item: 'Today paper lifecycle endpoint', ok: Boolean(trades?.ok), evidence: trades?.json?.count != null ? `count=${trades.json.count}` : String(trades?.status || trades?.error || '-') },
    { item: 'Gate/risk endpoint visible', ok: Boolean(gates?.ok), evidence: gates?.json?.status || gates?.status || gates?.error || '-' },
    { item: 'Live-money switch blocked until separate proof', ok: isLiveTradingBlocked(state?.json, broker?.json), evidence: isLiveTradingBlocked(state?.json, broker?.json) ? 'blocked' : 'enabled flag detected' },
  ]
  const readinessPass = readiness.every(r => r.ok)
  const overall = corePass && chainPass && noBadSource && readinessPass

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>End-to-End Visual Truth Proof</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
            Real broker/data truth only. Live money remains blocked until every row below passes.
          </div>
        </div>
        <button onClick={runProof} disabled={loading} style={{
          padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)',
          background: 'var(--surface-2)', color: 'var(--text-primary)', cursor: 'pointer'
        }}>{loading ? 'Checking read-only endpoints…' : 'Recheck Now'}</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(150px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card">{badge(overall, 'FULL E2E')}<div style={{ marginTop: 8, fontSize: 12 }}>Overall visual proof</div></div>
        <div className="card">{badge(corePass, 'API')}<div style={{ marginTop: 8, fontSize: 12 }}>Core endpoints</div></div>
        <div className="card">{badge(chainPass, 'DHAN CHAIN')}<div style={{ marginTop: 8, fontSize: 12 }}>Real Dhan option chain</div></div>
        <div className="card">{badge(noBadSource, 'NO BAD SOURCE')}<div style={{ marginTop: 8, fontSize: 12 }}>No non-Dhan/stale/fallback</div></div>
        <div className="card">{badge(readinessPass, 'TRADER READY')}<div style={{ marginTop: 8, fontSize: 12 }}>Human readiness checklist</div></div>
      </div>

      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 14 }}>
        Last run: {lastRun || 'not yet'} · This panel is proof-only; it does not enable live orders.
      </div>

      <h3 style={{ fontSize: 16 }}>Trader Readiness Truth Checklist</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, marginBottom: 18 }}>
        <thead><tr><th className="thead">Required for real-money trading</th><th className="thead">Status</th><th className="thead">Evidence visible to user</th></tr></thead>
        <tbody>
          {readiness.map(row => <tr key={row.item}>
            <td className="tcell"><b>{row.item}</b></td>
            <td className="tcell">{badge(row.ok)}</td>
            <td className="tcell">{String(row.evidence)}</td>
          </tr>)}
        </tbody>
      </table>

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
              <td className="tcell" style={{ color: ok ? 'var(--text-muted)' : 'var(--down)' }}>{ok ? 'REAL_DHAN_VISIBLE' : (p.error || blockedReason(p.json))}</td>
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
