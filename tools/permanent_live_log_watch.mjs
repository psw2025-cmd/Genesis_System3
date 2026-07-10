import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const outDir = path.join('reports', 'latest', 'permanent_live_log_watch')
fs.mkdirSync(outDir, { recursive: true })

const requiredSymbols = (process.env.SYSTEM3_REQUIRED_UNDERLYINGS || 'NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY').split(',').map(s => s.trim().toUpperCase()).filter(Boolean)
const optionalSymbols = (process.env.SYSTEM3_OPTIONAL_UNDERLYINGS || 'SENSEX').split(',').map(s => s.trim().toUpperCase()).filter(Boolean).filter(s => !requiredSymbols.includes(s))
const requiredChainEndpoints = requiredSymbols.map(s => `/api/chain/${s}`)
const optionalChainEndpoints = optionalSymbols.map(s => `/api/chain/${s}`)
const chainEndpoints = [...requiredChainEndpoints, ...optionalChainEndpoints]
const endpoints = [
  '/api/auth/status', '/api/deploy/info', '/api/health', '/api/state',
  '/api/broker/dhan/status', '/api/broker/funds', '/api/broker/holdings', '/api/broker/positions/live',
  ...chainEndpoints,
  '/api/gain_rank', '/api/scanner/top_contract_gainers?top_n=5', '/api/pnl', '/api/auto_gates'
]
const tabs = [
  ['truth', 'Truth Control'], ['genesis', 'Genesis Brain'], ['e2e_proof', 'E2E Proof'], ['overview', 'Overview'],
  ['chain', 'Option Chain'], ['signals', 'Signals'], ['paper', 'Paper Trades'], ['positions', 'Positions'],
  ['broker', 'Broker'], ['performance', 'Performance'], ['ml', 'ML Model'], ['gates', 'Live Gate']
]

// Keep this list focused on real forbidden data truth, not generic UI labels.
// A visible "Endpoint: /api/..." string is handled by dashboard_live_ui_proof;
// permanent_live_log_watch checks runtime/network truth and must not double-fail
// a tab that already has a valid screenshot and passing API endpoints.
const forbidden = [/csv_fallback/i, /STALE_CSV_FALLBACK/i, /synthetic/i, /fake/i, /mock/i, /bhavcopy/i, /yahoo/i, /Request failed with status code 401/i, /Loading funds/i, /Loading holdings/i, /Loading positions/i, /INTERNAL_UNVERIFIED/i]

function tryJson(text) { try { return JSON.parse(text) } catch { return null } }
function safeName(s) { return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '') }
function wait(ms) { return new Promise(resolve => setTimeout(resolve, ms)) }
function headers(apiKey) { return apiKey ? { 'X-API-Key': apiKey } : {} }
function optionalNoise(text) {
  return /ML performance fetch failed|ML comparison fetch failed|\/api\/ml\/performance|\/api\/ml\/compare|fonts\.gstatic\.com|googleapis\.com\/css|woff2|WebSocket connection.*\/ws\/stream|Error during WebSocket handshake/i.test(text || '')
}
function transientBrowser502(text) {
  return /status of 502|Request failed with status code 502|AxiosError.*502/i.test(text || '')
}
function scanForbidden(scope, text, blockers) {
  if (optionalNoise(text)) return
  for (const re of forbidden) if (re.test(text || '')) blockers.push(`${scope}:FORBIDDEN:${re}`)
}

async function fetchWithRetry(page, ep, attempts = 5) {
  let last = null
  for (let i = 0; i < attempts; i++) {
    const result = await page.evaluate(async ({ ep, apiKey }) => {
      try {
        const r = await fetch(ep, { credentials: 'include', headers: apiKey ? { 'X-API-Key': apiKey } : {} })
        const text = await r.text()
        return { ok: r.ok, status: r.status, body: text.slice(0, 200000) }
      } catch (err) {
        return { ok: false, status: 0, body: '', error: String(err) }
      }
    }, { ep, apiKey: key })
    last = result
    if (result.ok || ![0, 429, 502, 503, 504].includes(Number(result.status))) return result
    await wait([8000, 16000, 30000, 45000, 60000][i] || 60000)
  }
  return last
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
const context = await browser.newContext({ viewport: { width: 1366, height: 768 }, extraHTTPHeaders: headers(key) })
const page = await context.newPage()
const browserConsole = [], pageErrors = [], requestFailures = [], networkResponses = []
page.on('console', msg => browserConsole.push({ type: msg.type(), text: msg.text(), location: msg.location() }))
page.on('pageerror', err => pageErrors.push({ message: err.message, stack: err.stack }))
page.on('requestfailed', req => requestFailures.push({ url: req.url(), method: req.method(), failure: req.failure()?.errorText || null }))
page.on('response', res => { const url = res.url(); if (url.includes('/api/') || url.includes('/ui/')) networkResponses.push({ url, status: res.status(), ok: res.ok() }) })

const summary = { base, generated_at: new Date().toISOString(), required_symbols: requiredSymbols, optional_symbols: optionalSymbols, auth: { ok: false, status: 0 }, endpoints: [], chain_truth: [], browser_console_count: 0, page_error_count: 0, request_failure_count: 0, network_response_count: 0, screenshots: [], truth_control_visible: false, final_verdict: 'UNKNOWN', infra_blockers: [], trade_readiness_blockers: [], optional_data_blockers: [], blockers: [] }

try {
  await page.goto(`${base}/api/auth/status`, { waitUntil: 'networkidle', timeout: 90000 })
  if (key) {
    let auth = null
    for (let i = 0; i < 5; i++) {
      auth = await page.evaluate(async (apiKey) => {
        const r = await fetch('/api/auth/session', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey }, credentials: 'include', body: JSON.stringify({ api_key: apiKey }) })
        return { ok: r.ok, status: r.status, text: await r.text() }
      }, key)
      if (auth.ok || ![429, 502, 503, 504].includes(Number(auth.status))) break
      await wait([8000, 16000, 30000, 45000, 60000][i] || 60000)
    }
    summary.auth = { ok: auth.ok, status: auth.status }
    if (!auth.ok) summary.infra_blockers.push(`AUTH_FAIL:${auth.status}`)
  } else {
    summary.auth = { ok: false, status: 0, note: 'DASHBOARD_API_KEY secret not configured' }
    summary.infra_blockers.push('DASHBOARD_API_KEY_SECRET_MISSING')
  }

  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 90000 })
  for (const ep of endpoints) {
    await wait(2500)
    const result = await fetchWithRetry(page, ep, 5)
    const payload = tryJson(result.body)
    fs.writeFileSync(path.join(outDir, `${safeName(ep)}.txt`), result.body || result.error || '')
    const optional = optionalChainEndpoints.includes(ep)
    summary.endpoints.push({ endpoint: ep, ok: result.ok, status: result.status, optional, error: result.error || null })
    if (!result.ok) summary.infra_blockers.push(`API_FAIL:${ep}:${result.status}`)
    if (result.ok) scanForbidden(`API:${ep}`, result.body || result.error || '', summary.infra_blockers)
    if (ep.includes('/api/chain/')) {
      const ok = dhanChainOk(payload), safeBlocked = isSafeDhanBlocked(payload)
      const row = { endpoint: ep, ok, optional, safe_blocked: safeBlocked, source: payload?.data_source || payload?.source || null, priority: payload?.source_priority || null, status: payload?.status || null, spot: payload?.spot || 0, total_contracts: payload?.total_contracts || (Array.isArray(payload?.contracts) ? payload.contracts.length : 0), blocker: ok ? null : (payload?.blocked_reason || payload?.message || payload?.status || 'NOT_REAL_DHAN_CHAIN') }
      summary.chain_truth.push(row)
      if (!ok) {
        const msg = `CHAIN_NOT_TRADE_READY:${ep}:${row.blocker}`
        if (optional && safeBlocked) summary.optional_data_blockers.push(msg)
        else if (safeBlocked) summary.trade_readiness_blockers.push(msg)
        else summary.infra_blockers.push(msg)
      }
    }
  }
  for (const [id, title] of tabs) {
    try {
      await wait(1500)
      await page.locator(`button[title="${title}"]`).first().click({ timeout: 25000 })
      await page.waitForTimeout(4000)
      const body = await page.locator('body').innerText({ timeout: 15000 })
      fs.writeFileSync(path.join(outDir, `${id}.body.txt`), body)
      scanForbidden(`UI:${title}`, body, summary.infra_blockers)
      if (id === 'truth' && /System Truth Control|Money readiness|Live broker order execution must remain disabled/i.test(body)) summary.truth_control_visible = true
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
  if (!summary.truth_control_visible) summary.infra_blockers.push('TRUTH_CONTROL_NOT_VISIBLE')
} catch (err) {
  summary.infra_blockers.push(`TOP_LEVEL_EXCEPTION:${String(err).slice(0, 240)}`)
}

summary.browser_console_count = browserConsole.length
summary.page_error_count = pageErrors.length
summary.request_failure_count = requestFailures.length
summary.network_response_count = networkResponses.length
const restCoreOk = summary.endpoints.length > 0 && summary.endpoints.every(x => x.ok || x.optional)
for (const item of browserConsole) {
  const text = `${item.type} ${item.text}`
  if (optionalNoise(text)) summary.optional_data_blockers.push(`OPTIONAL_BROWSER_NOISE:${text.slice(0, 180)}`)
  else if (transientBrowser502(text) && restCoreOk) summary.optional_data_blockers.push(`TRANSIENT_BROWSER_502_AFTER_API_PASS:${text.slice(0, 180)}`)
  else if (/error/i.test(item.type) || /failed|error|exception|401|500|csv_fallback|synthetic|fallback|stale/i.test(text)) summary.infra_blockers.push(`BROWSER_CONSOLE:${text.slice(0, 180)}`)
}
for (const err of pageErrors) summary.infra_blockers.push(`PAGE_ERROR:${err.message}`)
for (const req of requestFailures) {
  const text = `${req.url}:${req.failure}`
  if (optionalNoise(text)) summary.optional_data_blockers.push(`OPTIONAL_REQUEST_FAILED:${text}`)
  else summary.infra_blockers.push(`REQUEST_FAILED:${text}`)
}
fs.writeFileSync(path.join(outDir, 'browser_console.json'), JSON.stringify(browserConsole, null, 2))
fs.writeFileSync(path.join(outDir, 'page_errors.json'), JSON.stringify(pageErrors, null, 2))
fs.writeFileSync(path.join(outDir, 'request_failures.json'), JSON.stringify(requestFailures, null, 2))
fs.writeFileSync(path.join(outDir, 'network_responses.json'), JSON.stringify(networkResponses, null, 2))
summary.blockers = [...summary.infra_blockers, ...summary.trade_readiness_blockers]
summary.final_verdict = summary.infra_blockers.length ? 'FAIL' : (summary.trade_readiness_blockers.length ? 'BLOCKED_NOT_TRADE_READY' : 'PASS')
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Permanent Live Log Watch', '', `Generated: ${summary.generated_at}`, `Base: ${summary.base}`, `Required symbols: ${summary.required_symbols.join(', ')}`, `Optional symbols: ${summary.optional_symbols.join(', ') || '-'}`, `Final verdict: **${summary.final_verdict}**`, `Truth control visible: **${summary.truth_control_visible}**`, '',
  '## Runtime Log Sources Captured', `- Browser console entries: ${summary.browser_console_count}`, `- Page errors: ${summary.page_error_count}`, `- Request failures: ${summary.request_failure_count}`, `- Network responses: ${summary.network_response_count}`, '',
  '## Dhan Chain Truth', ...summary.chain_truth.map(x => `- ${x.ok ? 'PASS' : (x.safe_blocked ? 'BLOCKED' : 'FAIL')} ${x.optional ? '(optional)' : '(required)'} ${x.endpoint} source=${x.source} priority=${x.priority} status=${x.status} spot=${x.spot} contracts=${x.total_contracts} blocker=${x.blocker || '-'}`), '',
  '## API Endpoints', ...summary.endpoints.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.optional ? '(optional)' : ''} ${x.endpoint}${x.error ? ` ${x.error}` : ''}`), '',
  '## Screenshots', ...summary.screenshots.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title} size=${x.size || 0}${x.error ? ` ${x.error}` : ''}`), '',
  '## Infrastructure Blockers', ...(summary.infra_blockers.length ? summary.infra_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Trading Readiness Blockers', ...(summary.trade_readiness_blockers.length ? summary.trade_readiness_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Optional Data Blockers', ...(summary.optional_data_blockers.length ? summary.optional_data_blockers.map(x => `- ${x}`) : ['- none'])
].join('\n'))
await browser.close()
if (summary.infra_blockers.length) { console.error(`PERMANENT_LIVE_LOG_WATCH_FAILED infra_blockers=${summary.infra_blockers.length}`); console.error(summary.infra_blockers.join('\n')); process.exit(1) }
if (summary.trade_readiness_blockers.length) { console.error(`PERMANENT_LIVE_LOG_WATCH_BLOCKED_NOT_TRADE_READY trade_blockers=${summary.trade_readiness_blockers.length}`); console.error(summary.trade_readiness_blockers.join('\n')) }
