import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

// Permanent public-readonly runtime watcher.
// Safety contract: anonymous GETs only; no dashboard credentials, sessions, writes,
// broker order APIs, or secret payloads.
const base = (process.env.DASHBOARD_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
const outDir = path.join('reports', 'latest', 'permanent_live_log_watch')
fs.mkdirSync(outDir, { recursive: true })

const requiredSymbols = (process.env.SYSTEM3_REQUIRED_UNDERLYINGS || 'NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY')
  .split(',').map(s => s.trim().toUpperCase()).filter(Boolean)
const optionalSymbols = (process.env.SYSTEM3_OPTIONAL_UNDERLYINGS || 'SENSEX')
  .split(',').map(s => s.trim().toUpperCase()).filter(Boolean)
  .filter(s => !requiredSymbols.includes(s))
const requiredChainEndpoints = requiredSymbols.map(s => `/api/chain/${s}`)
const optionalChainEndpoints = optionalSymbols.map(s => `/api/chain/${s}`)
const endpoints = [
  '/api/auth/status', '/api/deploy/info', '/api/health', '/api/state', '/api/broker/status',
  '/api/broker/funds', '/api/broker/holdings', '/api/broker/positions/live',
  ...requiredChainEndpoints, ...optionalChainEndpoints,
  '/api/gain_rank', '/api/scanner/top_contract_gainers?top_n=5', '/api/pnl', '/api/auto_gates'
]
const tabs = [
  ['truth', 'Truth Control'], ['genesis', 'Genesis Brain'], ['e2e_proof', 'E2E Proof'], ['overview', 'Overview'],
  ['chain', 'Option Chain'], ['signals', 'Signals'], ['paper', 'Paper Trades'], ['positions', 'Positions'],
  ['broker', 'Broker'], ['performance', 'Performance'], ['ml', 'ML Model'], ['gates', 'Live Gate']
]
const forbidden = [
  /csv_fallback/i, /STALE_CSV_FALLBACK/i, /INTERNAL_UNVERIFIED/i,
  /Request failed with status code 401/i, /Loading funds/i, /Loading holdings/i, /Loading positions/i
]
const provenanceWords = [/\bsynthetic\b/i, /\bfake\b/i, /\bmock\b/i]
const explicitRejection = /\b(reject(?:ed|ion)?|forbid(?:den)?|not allowed|must not|never use|disabled|blocked|excluded|no synthetic|no fake|no mock)\b/i

function tryJson(text) { try { return JSON.parse(text) } catch { return null } }
function safeName(s) { return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '') }
function wait(ms) { return new Promise(resolve => setTimeout(resolve, ms)) }
function optionalNoise(text) {
  return /ML performance fetch failed|ML comparison fetch failed|\/api\/ml\/performance|\/api\/ml\/compare|fonts\.gstatic\.com|googleapis\.com\/css|woff2|WebSocket connection.*\/ws\/stream|Error during WebSocket handshake/i.test(text || '')
}
function scanForbidden(scope, text, blockers) {
  if (optionalNoise(text)) return
  const value = text || ''
  for (const re of forbidden) if (re.test(value)) blockers.push(`${scope}:FORBIDDEN:${re}`)
  if (!scope.startsWith('UI:')) return
  for (const line of value.split(/\r?\n/)) {
    if (explicitRejection.test(line)) continue
    for (const re of provenanceWords) if (re.test(line)) blockers.push(`${scope}:FORBIDDEN:${re}`)
  }
}
async function anonymousFetch(page, ep, attempts = 3) {
  let last = null
  for (let i = 0; i < attempts; i++) {
    last = await page.evaluate(async (endpoint) => {
      try {
        const r = await fetch(endpoint, { method: 'GET', credentials: 'omit', cache: 'no-store' })
        return { ok: r.ok, status: r.status, body: (await r.text()).slice(0, 200000) }
      } catch (err) {
        return { ok: false, status: 0, body: '', error: String(err) }
      }
    }, ep)
    if (last.ok || ![0, 429, 502, 503, 504].includes(Number(last.status))) return last
    await wait([3000, 8000, 15000][i] || 15000)
  }
  return last
}
function dhanChainOk(payload) {
  if (!payload || typeof payload !== 'object' || payload.stale === true) return false
  const source = String(payload.data_source || payload.source || '').toLowerCase()
  const status = String(payload.status || '').toUpperCase()
  const contracts = Number(payload.total_contracts || (Array.isArray(payload.contracts) ? payload.contracts.length : 0))
  const spot = Number(payload.spot || 0)
  const allowedStatus = ['OK', 'MARKET_OPEN', 'MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT'].includes(status)
  return source === 'dhan' && allowedStatus && spot > 0 && contracts > 0
}
function safeDhanBlocked(payload) {
  if (!payload || typeof payload !== 'object') return false
  const source = String(payload.data_source || payload.source || '').toLowerCase()
  const status = String(payload.status || '').toUpperCase()
  const reason = String(payload.blocked_reason || payload.message || '').toUpperCase()
  return source === 'dhan' && status === 'NO_DHAN_DATA' && /NO_CURRENT|NO_DHAN|OPTION_CHAIN|ROWS/.test(reason)
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1366, height: 768 } })
const page = await context.newPage()
const browserConsole = [], pageErrors = [], requestFailures = [], networkResponses = []
page.on('console', msg => browserConsole.push({ type: msg.type(), text: msg.text(), location: msg.location() }))
page.on('pageerror', err => pageErrors.push({ message: err.message, stack: err.stack }))
page.on('requestfailed', req => requestFailures.push({ url: req.url(), method: req.method(), failure: req.failure()?.errorText || null }))
page.on('response', res => { if (res.url().includes('/api/') || res.url().includes('/ui/')) networkResponses.push({ url: res.url(), status: res.status(), ok: res.ok() }) })

const summary = {
  base, generated_at: new Date().toISOString(), required_symbols: requiredSymbols, optional_symbols: optionalSymbols,
  auth_contract: null, endpoints: [], chain_truth: [], screenshots: [], truth_control_visible: false,
  browser_console_count: 0, page_error_count: 0, request_failure_count: 0, network_response_count: 0,
  final_verdict: 'UNKNOWN', infra_blockers: [], trade_readiness_blockers: [], optional_data_blockers: [], blockers: []
}

try {
  const auth = await anonymousFetch(page, '/api/auth/status')
  const authPayload = tryJson(auth.body)
  summary.auth_contract = { ok: auth.ok, status: auth.status, mode: authPayload?.mode || null, required: authPayload?.required, credential_surface: authPayload?.credential_surface || null }
  if (!auth.ok || authPayload?.mode !== 'public_readonly' || authPayload?.required !== false || authPayload?.credential_surface !== 'REMOVED') {
    summary.infra_blockers.push('PUBLIC_READONLY_AUTH_CONTRACT_DRIFT')
  }

  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 90000 })
  for (const ep of endpoints) {
    const result = await anonymousFetch(page, ep)
    const payload = tryJson(result.body)
    fs.writeFileSync(path.join(outDir, `${safeName(ep)}.txt`), result.body || result.error || '')
    const optional = optionalChainEndpoints.includes(ep)
    summary.endpoints.push({ endpoint: ep, ok: result.ok, status: result.status, optional, error: result.error || null })
    if (!result.ok) summary.infra_blockers.push(`API_FAIL:${ep}:${result.status}`)
    if (result.ok) scanForbidden(`API:${ep}`, result.body || '', summary.infra_blockers)
    if (ep.includes('/api/chain/')) {
      const ok = dhanChainOk(payload), blocked = safeDhanBlocked(payload)
      const row = { endpoint: ep, ok, optional, safe_blocked: blocked, source: payload?.data_source || payload?.source || null, status: payload?.status || null, spot: payload?.spot || 0, total_contracts: payload?.total_contracts || (Array.isArray(payload?.contracts) ? payload.contracts.length : 0), blocker: ok ? null : (payload?.blocked_reason || payload?.message || payload?.status || 'NOT_REAL_DHAN_CHAIN') }
      summary.chain_truth.push(row)
      if (!ok) {
        const msg = `CHAIN_NOT_TRADE_READY:${ep}:${row.blocker}`
        if (optional && blocked) summary.optional_data_blockers.push(msg)
        else if (blocked) summary.trade_readiness_blockers.push(msg)
        else summary.infra_blockers.push(msg)
      }
    }
  }

  for (const [id, title] of tabs) {
    try {
      await page.locator(`button[title="${title}"]`).first().click({ timeout: 25000 })
      await page.waitForTimeout(2500)
      const body = await page.locator('body').innerText({ timeout: 15000 })
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
for (const item of browserConsole) {
  const text = `${item.type} ${item.text}`
  if (optionalNoise(text)) summary.optional_data_blockers.push(`OPTIONAL_BROWSER_NOISE:${text.slice(0, 180)}`)
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
  '# Permanent Live Log Watch', '', `Generated: ${summary.generated_at}`, `Base: ${summary.base}`, `Final verdict: **${summary.final_verdict}**`,
  `Public-readonly contract: **${summary.auth_contract?.ok && summary.auth_contract?.mode === 'public_readonly' && summary.auth_contract?.required === false && summary.auth_contract?.credential_surface === 'REMOVED' ? 'PASS' : 'FAIL'}**`,
  `Truth control visible: **${summary.truth_control_visible}**`, '',
  '## Dhan Chain Truth', ...summary.chain_truth.map(x => `- ${x.ok ? 'PASS' : (x.safe_blocked ? 'BLOCKED' : 'FAIL')} ${x.optional ? '(optional)' : '(required)'} ${x.endpoint} source=${x.source} status=${x.status} spot=${x.spot} contracts=${x.total_contracts} blocker=${x.blocker || '-'}`), '',
  '## API Endpoints', ...summary.endpoints.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.optional ? '(optional)' : ''} ${x.endpoint}`), '',
  '## Screenshots', ...summary.screenshots.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title} size=${x.size || 0}`), '',
  '## Infrastructure Blockers', ...(summary.infra_blockers.length ? summary.infra_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Trading Readiness Blockers', ...(summary.trade_readiness_blockers.length ? summary.trade_readiness_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Optional Data Blockers', ...(summary.optional_data_blockers.length ? summary.optional_data_blockers.map(x => `- ${x}`) : ['- none'])
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
