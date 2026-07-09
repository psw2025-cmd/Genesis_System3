import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const outDir = path.join('reports', 'latest', 'permanent_live_log_watch')
fs.mkdirSync(outDir, { recursive: true })

const endpoints = [
  '/api/auth/status',
  '/api/deploy/info',
  '/api/health',
  '/api/state',
  '/api/broker/dhan/status',
  '/api/broker/funds',
  '/api/broker/holdings',
  '/api/broker/positions/live',
  '/api/chain/NIFTY',
  '/api/chain/BANKNIFTY',
  '/api/chain/FINNIFTY',
  '/api/chain/MIDCPNIFTY',
  '/api/chain/SENSEX',
  '/api/gain_rank',
  '/api/pnl',
  '/api/auto_gates'
]

const tabs = [
  ['genesis', 'Genesis Brain'],
  ['e2e_proof', 'E2E Proof'],
  ['overview', 'Overview'],
  ['chain', 'Option Chain'],
  ['signals', 'Signals'],
  ['paper', 'Paper Trades'],
  ['positions', 'Positions'],
  ['broker', 'Broker'],
  ['performance', 'Performance'],
  ['ml', 'ML Model'],
  ['gates', 'Live Gate']
]

const forbidden = [
  /csv_fallback/i,
  /STALE_CSV_FALLBACK/i,
  /synthetic/i,
  /fake/i,
  /mock/i,
  /bhavcopy/i,
  /yahoo/i,
  /Request failed with status code 401/i,
  /Endpoint:\s*\/api\//i,
  /Loading funds/i,
  /Loading holdings/i,
  /Loading positions/i,
  /INTERNAL_UNVERIFIED/i,
]

function tryJson(text) {
  try { return JSON.parse(text) } catch { return null }
}

function safeName(s) {
  return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '')
}

function scanForbidden(scope, text, blockers) {
  for (const re of forbidden) {
    if (re.test(text || '')) blockers.push(`${scope}:FORBIDDEN:${re}`)
  }
}

function dhanChainOk(payload) {
  if (!payload || typeof payload !== 'object') return false
  const source = String(payload.data_source || payload.source || '').toLowerCase()
  const priority = String(payload.source_priority || '').toLowerCase()
  const status = String(payload.status || '').toUpperCase()
  const combined = `${source} ${priority} ${status}`
  if (payload.stale === true) return false
  if (/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock)/i.test(combined)) return false
  const contracts = Number(payload.total_contracts || (Array.isArray(payload.contracts) ? payload.contracts.length : 0))
  const spot = Number(payload.spot || 0)
  const allowedStatus = status === 'OK' || status === 'MARKET_OPEN' || status === 'MARKET_CLOSED_DHAN_SNAPSHOT' || status === 'EOD_SNAPSHOT'
  return source === 'dhan' && allowedStatus && spot > 0 && contracts > 0
}

function isSafeDhanBlocked(payload) {
  if (!payload || typeof payload !== 'object') return false
  const status = String(payload.status || '').toUpperCase()
  const reason = String(payload.blocked_reason || payload.message || '').toUpperCase()
  const source = String(payload.data_source || payload.source || '').toLowerCase()
  return source === 'dhan' && status === 'NO_DHAN_DATA' && /NO_CURRENT|NO_DHAN|OPTION_CHAIN|ROWS/.test(reason)
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1366, height: 768 } })
const page = await context.newPage()

const browserConsole = []
const pageErrors = []
const requestFailures = []
const networkResponses = []

page.on('console', msg => {
  browserConsole.push({ type: msg.type(), text: msg.text(), location: msg.location() })
})
page.on('pageerror', err => {
  pageErrors.push({ message: err.message, stack: err.stack })
})
page.on('requestfailed', req => {
  requestFailures.push({ url: req.url(), method: req.method(), failure: req.failure()?.errorText || null })
})
page.on('response', res => {
  const url = res.url()
  if (url.includes('/api/') || url.includes('/ui/')) {
    networkResponses.push({ url, status: res.status(), ok: res.ok() })
  }
})

const summary = {
  base,
  generated_at: new Date().toISOString(),
  auth: { ok: false, status: 0 },
  endpoints: [],
  chain_truth: [],
  browser_console_count: 0,
  page_error_count: 0,
  request_failure_count: 0,
  network_response_count: 0,
  screenshots: [],
  final_verdict: 'UNKNOWN',
  infra_blockers: [],
  trade_readiness_blockers: [],
  blockers: []
}

try {
  await page.goto(`${base}/api/auth/status`, { waitUntil: 'networkidle', timeout: 60000 })

  if (key) {
    const auth = await page.evaluate(async (apiKey) => {
      const r = await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ api_key: apiKey })
      })
      return { ok: r.ok, status: r.status, text: await r.text() }
    }, key)
    summary.auth = { ok: auth.ok, status: auth.status }
    if (!auth.ok) summary.infra_blockers.push(`AUTH_FAIL:${auth.status}`)
  } else {
    summary.auth = { ok: false, status: 0, note: 'DASHBOARD_API_KEY secret not configured' }
    summary.infra_blockers.push('DASHBOARD_API_KEY_SECRET_MISSING')
  }

  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 60000 })

  for (const ep of endpoints) {
    const result = await page.evaluate(async (ep) => {
      try {
        const r = await fetch(ep, { credentials: 'include' })
        const text = await r.text()
        return { ok: r.ok, status: r.status, body: text.slice(0, 200000) }
      } catch (err) {
        return { ok: false, status: 0, body: '', error: String(err) }
      }
    }, ep)
    const payload = tryJson(result.body)
    fs.writeFileSync(path.join(outDir, `${safeName(ep)}.txt`), result.body || result.error || '')
    summary.endpoints.push({ endpoint: ep, ok: result.ok, status: result.status, error: result.error || null })
    if (!result.ok) summary.infra_blockers.push(`API_FAIL:${ep}:${result.status}`)
    scanForbidden(`API:${ep}`, result.body || result.error || '', summary.infra_blockers)

    if (ep.includes('/api/chain/')) {
      const ok = dhanChainOk(payload)
      const safeBlocked = isSafeDhanBlocked(payload)
      const row = {
        endpoint: ep,
        ok,
        safe_blocked: safeBlocked,
        source: payload?.data_source || payload?.source || null,
        priority: payload?.source_priority || null,
        status: payload?.status || null,
        spot: payload?.spot || 0,
        total_contracts: payload?.total_contracts || (Array.isArray(payload?.contracts) ? payload.contracts.length : 0),
        blocker: ok ? null : (payload?.blocked_reason || payload?.message || payload?.status || 'NOT_REAL_DHAN_CHAIN')
      }
      summary.chain_truth.push(row)
      if (!ok) {
        const msg = `CHAIN_NOT_TRADE_READY:${ep}:${row.blocker}`
        if (safeBlocked) summary.trade_readiness_blockers.push(msg)
        else summary.infra_blockers.push(msg)
      }
    }
  }

  for (const [id, title] of tabs) {
    try {
      await page.locator(`button[title="${title}"]`).first().click({ timeout: 12000 })
      await page.waitForTimeout(3000)
      const body = await page.locator('body').innerText({ timeout: 10000 })
      fs.writeFileSync(path.join(outDir, `${id}.body.txt`), body)
      scanForbidden(`UI:${title}`, body, summary.infra_blockers)
      const screenshot = path.join(outDir, `${id}.png`)
      await page.screenshot({ path: screenshot, fullPage: true })
      const ok = fs.existsSync(screenshot) && fs.statSync(screenshot).size > 10000
      summary.screenshots.push({ id, title, ok, path: screenshot, size: ok ? fs.statSync(screenshot).size : 0 })
      if (!ok) summary.infra_blockers.push(`SCREENSHOT_MISSING_OR_EMPTY:${title}`)
    } catch (err) {
      summary.screenshots.push({ id, title, ok: false, error: String(err) })
      summary.infra_blockers.push(`UI_TAB_EXCEPTION:${title}:${String(err).slice(0, 160)}`)
    }
  }
} catch (err) {
  summary.infra_blockers.push(`TOP_LEVEL_EXCEPTION:${String(err).slice(0, 240)}`)
}

summary.browser_console_count = browserConsole.length
summary.page_error_count = pageErrors.length
summary.request_failure_count = requestFailures.length
summary.network_response_count = networkResponses.length

for (const item of browserConsole) {
  const text = `${item.type} ${item.text}`
  if (/error/i.test(item.type) || /failed|error|exception|401|500|csv_fallback|synthetic|fallback|stale/i.test(text)) {
    summary.infra_blockers.push(`BROWSER_CONSOLE:${text.slice(0, 180)}`)
  }
}
for (const err of pageErrors) summary.infra_blockers.push(`PAGE_ERROR:${err.message}`)
for (const req of requestFailures) summary.infra_blockers.push(`REQUEST_FAILED:${req.url}:${req.failure}`)

fs.writeFileSync(path.join(outDir, 'browser_console.json'), JSON.stringify(browserConsole, null, 2))
fs.writeFileSync(path.join(outDir, 'page_errors.json'), JSON.stringify(pageErrors, null, 2))
fs.writeFileSync(path.join(outDir, 'request_failures.json'), JSON.stringify(requestFailures, null, 2))
fs.writeFileSync(path.join(outDir, 'network_responses.json'), JSON.stringify(networkResponses, null, 2))

summary.blockers = [...summary.infra_blockers, ...summary.trade_readiness_blockers]
summary.final_verdict = summary.infra_blockers.length ? 'FAIL' : (summary.trade_readiness_blockers.length ? 'BLOCKED_NOT_TRADE_READY' : 'PASS')
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Permanent Live Log Watch',
  '',
  `Generated: ${summary.generated_at}`,
  `Base: ${summary.base}`,
  `Final verdict: **${summary.final_verdict}**`,
  '',
  '## Runtime Log Sources Captured',
  `- Browser console entries: ${summary.browser_console_count}`,
  `- Page errors: ${summary.page_error_count}`,
  `- Request failures: ${summary.request_failure_count}`,
  `- Network responses: ${summary.network_response_count}`,
  '',
  '## Dhan Chain Truth',
  ...summary.chain_truth.map(x => `- ${x.ok ? 'PASS' : (x.safe_blocked ? 'BLOCKED' : 'FAIL')} ${x.endpoint} source=${x.source} priority=${x.priority} status=${x.status} spot=${x.spot} contracts=${x.total_contracts} blocker=${x.blocker || '-'}`),
  '',
  '## API Endpoints',
  ...summary.endpoints.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.endpoint}${x.error ? ` ${x.error}` : ''}`),
  '',
  '## Screenshots',
  ...summary.screenshots.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title} size=${x.size || 0}${x.error ? ` ${x.error}` : ''}`),
  '',
  '## Infrastructure Blockers',
  ...(summary.infra_blockers.length ? summary.infra_blockers.map(x => `- ${x}`) : ['- none']),
  '',
  '## Trading Readiness Blockers',
  ...(summary.trade_readiness_blockers.length ? summary.trade_readiness_blockers.map(x => `- ${x}`) : ['- none'])
].join('\n'))

await browser.close()

if (summary.infra_blockers.length) {
  console.error(`PERMANENT_LIVE_LOG_WATCH_FAILED infra_blockers=${summary.infra_blockers.length}`)
  console.error(summary.infra_blockers.join('\n'))
  process.exit(1)
}

if (summary.trade_readiness_blockers.length) {
  console.error(`PERMANENT_LIVE_LOG_WATCH_BLOCKED_NOT_TRADE_READY trade_blockers=${summary.trade_readiness_blockers.length}`)
  console.error(summary.trade_readiness_blockers.join('\n'))
}
