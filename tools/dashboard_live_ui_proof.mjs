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
  if (/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock|stale)/i.test(combined)) return false
  const contracts = Array.isArray(payload.contracts) ? payload.contracts.length : Number(payload.total_contracts || 0)
  const spot = Number(payload.spot || 0)
  return source === 'dhan' && contracts > 0 && spot > 0
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
  final_verdict: 'UNKNOWN',
  blockers: [],
}

await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 60000 })

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
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify(summary.auth, null, 2))
  await page.reload({ waitUntil: 'networkidle', timeout: 60000 })
} else {
  summary.auth = { ok: false, status: 0, note: 'DASHBOARD_API_KEY secret not configured' }
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify(summary.auth, null, 2))
}

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
    const chainRow = {
      endpoint: ep,
      ok,
      source: payload?.data_source || payload?.source || null,
      source_priority: payload?.source_priority || null,
      status: payload?.status || null,
      stale: payload?.stale === true,
      spot: payload?.spot || 0,
      total_contracts: payload?.total_contracts || (Array.isArray(payload?.contracts) ? payload.contracts.length : 0),
      blocker: ok ? null : (payload?.blocked_reason || payload?.message || payload?.status || 'NOT_REAL_DHAN_CHAIN')
    }
    summary.chain_truth.push(chainRow)
    if (!ok) summary.blockers.push(`CHAIN_NOT_REAL_DHAN:${ep}:${chainRow.blocker}`)
  }

  if (!result.ok) summary.blockers.push(`API_FAIL:${ep}:${result.status}`)
}

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

for (const [id, title] of tabs) {
  try {
    const btn = page.locator(`button[title="${title}"]`).first()
    await btn.click({ timeout: 10000 })
    await page.waitForTimeout(3000)
    const text = await page.locator('body').innerText({ timeout: 10000 })
    const bad = /Endpoint:\s*\/api\/|Request failed with status code 401|Loading funds|Loading holdings|Loading positions/.test(text)
    const screenshotPath = path.join(outDir, `${id}.png`)
    await page.screenshot({ path: screenshotPath, fullPage: true })
    const screenshotOk = fs.existsSync(screenshotPath) && fs.statSync(screenshotPath).size > 10000
    const e2eHasProofWords = id !== 'e2e_proof' || /End-to-End Visual Truth Proof|Dhan Option Chain Proof|Core API/.test(text)
    const ok = !bad && screenshotOk && e2eHasProofWords
    summary.ui.push({ id, title, ok, bad_raw_error_or_loading: bad, screenshot_ok: screenshotOk, e2e_has_proof_words: e2eHasProofWords })
    if (!ok) summary.blockers.push(`UI_FAIL:${title}`)
  } catch (err) {
    summary.ui.push({ id, title, ok: false, error: String(err) })
    summary.blockers.push(`UI_EXCEPTION:${title}:${String(err).slice(0, 160)}`)
  }
}

await page.setViewportSize({ width: 390, height: 844 })
await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(3000)
const mobilePath = path.join(outDir, 'mobile_390x844.png')
await page.screenshot({ path: mobilePath, fullPage: true })
if (!fs.existsSync(mobilePath) || fs.statSync(mobilePath).size <= 10000) summary.blockers.push('MOBILE_SCREENSHOT_MISSING_OR_EMPTY')

summary.final_verdict = summary.blockers.length === 0 ? 'PASS' : 'FAIL'
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Dashboard Live UI Proof',
  '',
  `Generated: ${summary.generated_at}`,
  `Base: ${base}`,
  `Final verdict: **${summary.final_verdict}**`,
  '',
  '## Chain Truth',
  ...summary.chain_truth.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.endpoint} source=${x.source} priority=${x.source_priority} status=${x.status} spot=${x.spot} contracts=${x.total_contracts} blocker=${x.blocker || '-'}`),
  '',
  '## API',
  ...summary.api.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.endpoint}`),
  '',
  '## UI Screenshots',
  ...summary.ui.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title}${x.error ? ` - ${x.error}` : ''}`),
  '',
  '## Blockers',
  ...(summary.blockers.length ? summary.blockers.map(x => `- ${x}`) : ['- none'])
].join('\n'))

await browser.close()

if (summary.final_verdict !== 'PASS') {
  console.error(`DASHBOARD_LIVE_UI_PROOF_FAILED blockers=${summary.blockers.length}`)
  console.error(summary.blockers.join('\n'))
  process.exit(1)
}
