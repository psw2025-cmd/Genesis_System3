import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const outDir = path.join('reports', 'latest', 'dashboard_live_ui_proof')
fs.mkdirSync(outDir, { recursive: true })

const chainEndpoints = [
  '/api/chain/NIFTY',
  '/api/chain/BANKNIFTY',
  '/api/chain/FINNIFTY',
  '/api/chain/MIDCPNIFTY',
  '/api/chain/SENSEX',
]

const apiEndpoints = [
  '/api/auth/status',
  '/api/deploy/info',
  '/api/health',
  '/api/state',
  '/api/broker/dhan/status',
  '/api/broker/funds',
  '/api/broker/holdings',
  '/api/broker/positions/live',
  ...chainEndpoints,
  '/api/gain_rank',
  '/api/pnl',
  '/api/trades/today',
  '/api/auto_gates'
]

function safeName(s) {
  return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '')
}

function tryJson(text) {
  try { return JSON.parse(text) } catch { return { raw: String(text || '').slice(0, 2000) } }
}

function dhanChainOk(payload) {
  if (!payload || typeof payload !== 'object') return false
  const source = String(payload.data_source || payload.source || '').toLowerCase()
  const priority = String(payload.source_priority || '').toLowerCase()
  const status = String(payload.status || '').toUpperCase()
  const combined = `${source} ${priority} ${status}`
  if (payload.stale === true) return false
  if (/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock)/i.test(combined)) return false
  const contracts = Array.isArray(payload.contracts) ? payload.contracts.length : Number(payload.total_contracts || 0)
  const spot = Number(payload.spot || 0)
  const allowedStatus = status === 'OK' || status === 'MARKET_OPEN' || status === 'MARKET_CLOSED_DHAN_SNAPSHOT' || status === 'EOD_SNAPSHOT'
  return source === 'dhan' && allowedStatus && contracts > 0 && spot > 0
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

const summary = {
  base,
  generated_at: new Date().toISOString(),
  auth: { ok: false, status: 0 },
  api: [],
  ui: [],
  chain_truth: [],
  trader_readiness_panel_visible: false,
  truth_control_visible: false,
  final_verdict: 'UNKNOWN',
  infra_blockers: [],
  trade_readiness_blockers: [],
  blockers: [],
}

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
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify(summary.auth, null, 2))
} else {
  summary.auth = { ok: false, status: 0, note: 'DASHBOARD_API_KEY secret not configured' }
  summary.infra_blockers.push('DASHBOARD_API_KEY_SECRET_MISSING')
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify(summary.auth, null, 2))
}

await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 60000 })

for (const ep of apiEndpoints) {
  const result = await page.evaluate(async (ep) => {
    try {
      const r = await fetch(ep, { credentials: 'include' })
      const text = await r.text()
      return { endpoint: ep, ok: r.ok, status: r.status, body: text.slice(0, 200000) }
    } catch (err) {
      return { endpoint: ep, ok: false, status: 0, error: String(err) }
    }
  }, ep)
  const payload = tryJson(result.body || '')
  const apiRow = { endpoint: ep, ok: result.ok, status: result.status }
  summary.api.push(apiRow)
  fs.writeFileSync(path.join(outDir, `${safeName(ep)}.json`), JSON.stringify(payload, null, 2))

  if (chainEndpoints.includes(ep)) {
    const ok = result.ok && dhanChainOk(payload)
    const safeBlocked = result.ok && isSafeDhanBlocked(payload)
    const chainRow = {
      endpoint: ep,
      ok,
      safe_blocked: safeBlocked,
      source: payload?.data_source || payload?.source || null,
      source_priority: payload?.source_priority || null,
      status: payload?.status || null,
      stale: payload?.stale === true,
      spot: payload?.spot || 0,
      total_contracts: payload?.total_contracts || (Array.isArray(payload?.contracts) ? payload.contracts.length : 0),
      blocker: ok ? null : (payload?.blocked_reason || payload?.message || payload?.status || 'NOT_REAL_DHAN_CHAIN')
    }
    summary.chain_truth.push(chainRow)
    if (!ok) {
      const msg = `CHAIN_NOT_TRADE_READY:${ep}:${chainRow.blocker}`
      if (safeBlocked) summary.trade_readiness_blockers.push(msg)
      else summary.infra_blockers.push(msg)
    }
  }

  if (!result.ok) summary.infra_blockers.push(`API_FAIL:${ep}:${result.status}`)
}

const tabs = [
  ['truth', 'Truth Control'],
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

for (const [id, title] of tabs) {
  try {
    const btn = page.locator(`button[title="${title}"]`).first()
    await btn.click({ timeout: 10000 })
    await page.waitForTimeout(3000)
    const text = await page.locator('body').innerText({ timeout: 10000 })
    const bad = /Endpoint:\s*\/api\/|Request failed with status code 401|Loading funds|Loading holdings|Loading positions|hardcoded 0|\.\.\.3741|cached read-only/i.test(text)
    const screenshotPath = path.join(outDir, `${id}.png`)
    await page.screenshot({ path: screenshotPath, fullPage: true })
    const screenshotOk = fs.existsSync(screenshotPath) && fs.statSync(screenshotPath).size > 10000
    const e2eHasProofWords = id !== 'e2e_proof' || /Trader Readiness Truth Checklist|Required for real-money trading|Live-money switch blocked/i.test(text)
    const truthHasProofWords = id !== 'truth' || /System Truth Control|Money readiness|Live broker order execution must remain disabled/i.test(text)
    if (id === 'e2e_proof' && e2eHasProofWords) summary.trader_readiness_panel_visible = true
    if (id === 'truth' && truthHasProofWords) summary.truth_control_visible = true
    const ok = !bad && screenshotOk && e2eHasProofWords && truthHasProofWords
    summary.ui.push({ id, title, ok, bad_raw_error_or_loading: bad, screenshot_ok: screenshotOk, e2e_has_trader_readiness: e2eHasProofWords, truth_control_visible: truthHasProofWords })
    if (!ok) summary.infra_blockers.push(`UI_FAIL:${title}`)
  } catch (err) {
    summary.ui.push({ id, title, ok: false, error: String(err) })
    summary.infra_blockers.push(`UI_EXCEPTION:${title}:${String(err).slice(0, 160)}`)
  }
}

if (!summary.trader_readiness_panel_visible) summary.infra_blockers.push('TRADER_READINESS_PANEL_NOT_VISIBLE')
if (!summary.truth_control_visible) summary.infra_blockers.push('TRUTH_CONTROL_NOT_VISIBLE')

await page.setViewportSize({ width: 390, height: 844 })
await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(3000)
const mobilePath = path.join(outDir, 'mobile_390x844.png')
await page.screenshot({ path: mobilePath, fullPage: true })
if (!fs.existsSync(mobilePath) || fs.statSync(mobilePath).size <= 10000) summary.infra_blockers.push('MOBILE_SCREENSHOT_MISSING_OR_EMPTY')

summary.blockers = [...summary.infra_blockers, ...summary.trade_readiness_blockers]
summary.final_verdict = summary.infra_blockers.length ? 'FAIL' : (summary.trade_readiness_blockers.length ? 'BLOCKED_NOT_TRADE_READY' : 'PASS')
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Dashboard Live UI Proof',
  '',
  `Generated: ${summary.generated_at}`,
  `Base: ${base}`,
  `Final verdict: **${summary.final_verdict}**`,
  `Trader readiness panel visible: **${summary.trader_readiness_panel_visible}**`,
  `Truth control visible: **${summary.truth_control_visible}**`,
  '',
  '## Chain Truth',
  ...summary.chain_truth.map(x => `- ${x.ok ? 'PASS' : (x.safe_blocked ? 'BLOCKED' : 'FAIL')} ${x.endpoint} source=${x.source} priority=${x.source_priority} status=${x.status} spot=${x.spot} contracts=${x.total_contracts} blocker=${x.blocker || '-'}`),
  '',
  '## API',
  ...summary.api.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.endpoint}`),
  '',
  '## UI Screenshots',
  ...summary.ui.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title}${x.error ? ` - ${x.error}` : ''}`),
  '',
  '## Infrastructure Blockers',
  ...(summary.infra_blockers.length ? summary.infra_blockers.map(x => `- ${x}`) : ['- none']),
  '',
  '## Trading Readiness Blockers',
  ...(summary.trade_readiness_blockers.length ? summary.trade_readiness_blockers.map(x => `- ${x}`) : ['- none'])
].join('\n'))

await browser.close()

if (summary.infra_blockers.length) {
  console.error(`DASHBOARD_LIVE_UI_PROOF_FAILED infra_blockers=${summary.infra_blockers.length}`)
  console.error(summary.infra_blockers.join('\n'))
  process.exit(1)
}

if (summary.trade_readiness_blockers.length) {
  console.error(`DASHBOARD_LIVE_UI_PROOF_BLOCKED_NOT_TRADE_READY trade_blockers=${summary.trade_readiness_blockers.length}`)
  console.error(summary.trade_readiness_blockers.join('\n'))
}
