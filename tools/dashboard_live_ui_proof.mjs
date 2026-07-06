import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const outDir = path.join('reports', 'latest', 'dashboard_live_ui_proof')
fs.mkdirSync(outDir, { recursive: true })

const apiEndpoints = [
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

function safeName(s) {
  return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '')
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1366, height: 768 } })
const page = await context.newPage()

const summary = { base, generated_at: new Date().toISOString(), api: [], ui: [] }

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
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify({ ok: auth.ok, status: auth.status }, null, 2))
  await page.reload({ waitUntil: 'networkidle', timeout: 60000 })
} else {
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify({ ok: false, status: 0, note: 'DASHBOARD_API_KEY secret not configured' }, null, 2))
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
  summary.api.push({ endpoint: ep, ok: result.ok, status: result.status })
  fs.writeFileSync(path.join(outDir, `${safeName(ep)}.json`), result.body || JSON.stringify(result, null, 2))
}

const tabs = [
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
    await page.screenshot({ path: path.join(outDir, `${id}.png`), fullPage: true })
    summary.ui.push({ id, title, ok: !bad, bad_raw_error_or_loading: bad })
  } catch (err) {
    summary.ui.push({ id, title, ok: false, error: String(err) })
  }
}

await page.setViewportSize({ width: 390, height: 844 })
await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(3000)
await page.screenshot({ path: path.join(outDir, 'mobile_390x844.png'), fullPage: true })

fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Dashboard Live UI Proof',
  '',
  `Generated: ${summary.generated_at}`,
  `Base: ${base}`,
  '',
  '## API',
  ...summary.api.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.endpoint}`),
  '',
  '## UI',
  ...summary.ui.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title}${x.error ? ` - ${x.error}` : ''}`)
].join('\n'))

await browser.close()
