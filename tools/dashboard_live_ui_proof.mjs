import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const outDir = path.join('reports', 'latest', 'dashboard_live_ui_proof')
fs.mkdirSync(outDir, { recursive: true })

const requiredSymbols = (process.env.SYSTEM3_REQUIRED_UNDERLYINGS || 'NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY').split(',').map(s => s.trim().toUpperCase()).filter(Boolean)
const optionalSymbols = (process.env.SYSTEM3_OPTIONAL_UNDERLYINGS || 'SENSEX').split(',').map(s => s.trim().toUpperCase()).filter(Boolean).filter(s => !requiredSymbols.includes(s))
const requiredChainEndpoints = requiredSymbols.map(s => `/api/chain/${s}`)
const optionalChainEndpoints = optionalSymbols.map(s => `/api/chain/${s}`)
const chainEndpoints = [...requiredChainEndpoints, ...optionalChainEndpoints]
const apiEndpoints = [
  '/api/auth/status', '/api/deploy/info', '/api/health', '/api/state',
  '/api/broker/dhan/status', '/api/broker/funds', '/api/broker/holdings', '/api/broker/positions/live',
  ...chainEndpoints,
  '/api/gain_rank', '/api/scanner/top_contract_gainers?top_n=5', '/api/pnl', '/api/trades/today', '/api/auto_gates', '/api/ml/performance', '/api/ml/compare', '/api/paper'
]

function safeName(s) { return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '') }
function tryJson(text) { try { return JSON.parse(text) } catch { return { raw: String(text || '').slice(0, 2000) } } }
function wait(ms) { return new Promise(resolve => setTimeout(resolve, ms)) }
function headers(apiKey) { return apiKey ? { 'X-API-Key': apiKey } : {} }
function hasUiFailureText(text) { return /Request failed with status code 401|Loading funds|Loading holdings|Loading positions|hardcoded 0|\.\.\.3741|cached read-only/i.test(text || '') }
function hasOwner(text) { return /PRITAM\s+S\.?\s+WARGHADE/i.test(text || '') && /OWNER/i.test(text || '') }
function hasSafetyText(text) { return /LIVE\s+OFF/i.test(text || '') && /PAPER/i.test(text || '') }
function hasMlProofText(text) { return /ML Model Truth/i.test(text || '') && /Training status/i.test(text || '') && /Proof records/i.test(text || '') && /(MODEL_NOT_PROVEN|MODEL_PROOF_READY|PROVEN|BLOCKED)/i.test(text || '') }
function hasPaperTruthText(text) { return /Paper Truth Provenance/i.test(text || '') && /Fake\/fixture rejected/i.test(text || '') && /Order endpoints/i.test(text || '') && /(NOT CALLED|BLOCKED)/i.test(text || '') }
function solutionFor(blocker) {
  const b = String(blocker || '')
  if (b.includes('OWNER_BADGE_NOT_VISIBLE')) return 'Ensure TopBar renders OWNER / PRITAM S. WARGHADE in desktop and mobile screenshots, then rerun visual proof.'
  if (b.includes('SAFETY_LABELS_NOT_VISIBLE')) return 'Ensure TopBar shows PAPER and LIVE OFF in every screenshot.'
  if (b.includes('ML_PROOF_TEXT_NOT_VISIBLE')) return 'Ensure ML tab displays Proof records, Training status, model score/accuracy/AUC or a clear BLOCKED reason from /api/ml/performance.'
  if (b.includes('PAPER_TRUTH_NOT_VISIBLE')) return 'Ensure Paper tab displays Paper Truth Provenance, rejected fake/fixture rows, source file, displayed rows, and order endpoints NOT CALLED.'
  if (b.includes('SCREENSHOT_MISSING_OR_EMPTY')) return 'Fix Playwright screenshot capture, route load, or tab selector; screenshot file must exist and be >10KB.'
  if (b.includes('API_FAIL')) return 'Fix API endpoint/auth/rate-limit/deploy issue before claiming dashboard visual proof.'
  if (b.includes('CHAIN_NOT_TRADE_READY')) return 'Fix Dhan chain/expiry/security-id data path; optional chains may be safe-blocked, required chains cannot.'
  if (b.includes('UI_FAIL') || b.includes('UI_EXCEPTION')) return 'Fix UI route, tab rendering, loading state, or browser exception; rerun visual proof.'
  return 'Investigate exact blocker, patch source, redeploy, and regenerate dashboard visual proof before claiming resolved.'
}

async function pageFetchJson(page, ep, attempts = 5) {
  let last = null
  for (let i = 0; i < attempts; i++) {
    const result = await page.evaluate(async ({ ep, apiKey }) => {
      try {
        const r = await fetch(ep, { credentials: 'include', headers: apiKey ? { 'X-API-Key': apiKey } : {} })
        const text = await r.text()
        return { endpoint: ep, ok: r.ok, status: r.status, body: text.slice(0, 200000) }
      } catch (err) {
        return { endpoint: ep, ok: false, status: 0, error: String(err), body: '' }
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
const context = await browser.newContext({ viewport: { width: 1366, height: 768 }, extraHTTPHeaders: headers(key) })
const page = await context.newPage()

const summary = { base, generated_at: new Date().toISOString(), required_symbols: requiredSymbols, optional_symbols: optionalSymbols, auth: { ok: false, status: 0 }, api: [], ui: [], visual_requirements: [], chain_truth: [], trader_readiness_panel_visible: false, truth_control_visible: false, owner_badge_visible: false, safety_labels_visible: false, ml_proof_visible: false, paper_truth_visible: false, final_verdict: 'UNKNOWN', infra_blockers: [], trade_readiness_blockers: [], visual_blockers: [], optional_data_blockers: [], blockers: [], solutions: [] }

function addVisualReq(id, ok, blocker, details = {}) {
  summary.visual_requirements.push({ id, ok, blocker: ok ? null : blocker, ...details })
  if (!ok) summary.visual_blockers.push(blocker)
}

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
  fs.writeFileSync(path.join(outDir, 'auth_session.json'), JSON.stringify(summary.auth, null, 2))

  for (const ep of apiEndpoints) {
    await wait(2500)
    const result = await pageFetchJson(page, ep, 5)
    const payload = tryJson(result.body || '')
    const optional = optionalChainEndpoints.includes(ep)
    summary.api.push({ endpoint: ep, ok: result.ok, status: result.status, optional })
    fs.writeFileSync(path.join(outDir, `${safeName(ep)}.json`), JSON.stringify(payload, null, 2))

    if (chainEndpoints.includes(ep)) {
      const ok = result.ok && dhanChainOk(payload)
      const safeBlocked = result.ok && isSafeDhanBlocked(payload)
      const chainRow = { endpoint: ep, ok, optional, safe_blocked: safeBlocked, source: payload?.data_source || payload?.source || null, source_priority: payload?.source_priority || null, status: payload?.status || null, stale: payload?.stale === true, spot: payload?.spot || 0, total_contracts: payload?.total_contracts || (Array.isArray(payload?.contracts) ? payload.contracts.length : 0), blocker: ok ? null : (payload?.blocked_reason || payload?.message || payload?.status || 'NOT_REAL_DHAN_CHAIN') }
      summary.chain_truth.push(chainRow)
      if (!ok) {
        const msg = `CHAIN_NOT_TRADE_READY:${ep}:${chainRow.blocker}`
        if (optional && safeBlocked) summary.optional_data_blockers.push(msg)
        else if (safeBlocked) summary.trade_readiness_blockers.push(msg)
        else summary.infra_blockers.push(msg)
      }
    }

    if (!result.ok) summary.infra_blockers.push(`API_FAIL:${ep}:${result.status}`)
  }

  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 90000 })
  await wait(5000)

  const tabs = [
    ['truth', 'Truth Control'], ['genesis', 'Genesis Brain'], ['e2e_proof', 'E2E Proof'], ['overview', 'Overview'],
    ['chain', 'Option Chain'], ['signals', 'Signals'], ['paper', 'Paper Trades'], ['positions', 'Positions'],
    ['broker', 'Broker'], ['performance', 'Performance'], ['ml', 'ML Model'], ['gates', 'Live Gate']
  ]

  for (const [id, title] of tabs) {
    try {
      await wait(1500)
      const btn = page.locator(`button[title="${title}"]`).first()
      await btn.click({ timeout: 25000 })
      await page.waitForTimeout(4500)
      const text = await page.locator('body').innerText({ timeout: 15000 })
      const bad = hasUiFailureText(text)
      const screenshotPath = path.join(outDir, `${id}.png`)
      await page.screenshot({ path: screenshotPath, fullPage: true })
      const screenshotOk = fs.existsSync(screenshotPath) && fs.statSync(screenshotPath).size > 10000
      const e2eHasProofWords = id !== 'e2e_proof' || /Trader Readiness Truth Checklist|Required for real-money trading|Live-money switch blocked/i.test(text)
      const truthHasProofWords = id !== 'truth' || /System Truth Control|Money readiness|Live broker order execution must remain disabled/i.test(text)
      const ownerVisible = hasOwner(text)
      const safetyVisible = hasSafetyText(text)
      const mlVisible = id !== 'ml' || hasMlProofText(text)
      const paperVisible = id !== 'paper' || hasPaperTruthText(text)
      if (ownerVisible) summary.owner_badge_visible = true
      if (safetyVisible) summary.safety_labels_visible = true
      if (id === 'ml' && mlVisible) summary.ml_proof_visible = true
      if (id === 'paper' && paperVisible) summary.paper_truth_visible = true
      if (id === 'e2e_proof' && e2eHasProofWords) summary.trader_readiness_panel_visible = true
      if (id === 'truth' && truthHasProofWords) summary.truth_control_visible = true
      const ok = !bad && screenshotOk && e2eHasProofWords && truthHasProofWords && ownerVisible && safetyVisible && mlVisible && paperVisible
      summary.ui.push({ id, title, ok, bad_raw_error_or_loading: bad, screenshot_ok: screenshotOk, owner_visible: ownerVisible, safety_labels_visible: safetyVisible, ml_proof_visible: mlVisible, paper_truth_visible: paperVisible, e2e_has_trader_readiness: e2eHasProofWords, truth_control_visible: truthHasProofWords })
      if (!screenshotOk) summary.visual_blockers.push(`SCREENSHOT_MISSING_OR_EMPTY:${title}`)
      if (!ownerVisible) summary.visual_blockers.push(`OWNER_BADGE_NOT_VISIBLE:${title}`)
      if (!safetyVisible) summary.visual_blockers.push(`SAFETY_LABELS_NOT_VISIBLE:${title}`)
      if (!mlVisible) summary.visual_blockers.push(`ML_PROOF_TEXT_NOT_VISIBLE:${title}`)
      if (!paperVisible) summary.visual_blockers.push(`PAPER_TRUTH_NOT_VISIBLE:${title}`)
      if (!ok) summary.infra_blockers.push(`UI_FAIL:${title}`)
    } catch (err) {
      summary.ui.push({ id, title, ok: false, error: String(err) })
      summary.infra_blockers.push(`UI_EXCEPTION:${title}:${String(err).slice(0, 160)}`)
    }
  }

  if (!summary.trader_readiness_panel_visible) summary.infra_blockers.push('TRADER_READINESS_PANEL_NOT_VISIBLE')
  if (!summary.truth_control_visible) summary.infra_blockers.push('TRUTH_CONTROL_NOT_VISIBLE')
  addVisualReq('OWNER_BADGE_VISIBLE', summary.owner_badge_visible, 'OWNER_BADGE_NOT_VISIBLE:GLOBAL')
  addVisualReq('SAFETY_LABELS_VISIBLE', summary.safety_labels_visible, 'SAFETY_LABELS_NOT_VISIBLE:GLOBAL')
  addVisualReq('ML_PROOF_VISIBLE', summary.ml_proof_visible, 'ML_PROOF_TEXT_NOT_VISIBLE:GLOBAL')
  addVisualReq('PAPER_TRUTH_VISIBLE', summary.paper_truth_visible, 'PAPER_TRUTH_NOT_VISIBLE:GLOBAL')

  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 90000 })
  await page.waitForTimeout(5000)
  const mobileText = await page.locator('body').innerText({ timeout: 15000 }).catch(() => '')
  const mobilePath = path.join(outDir, 'mobile_390x844.png')
  await page.screenshot({ path: mobilePath, fullPage: true })
  const mobileOk = fs.existsSync(mobilePath) && fs.statSync(mobilePath).size > 10000
  if (!mobileOk) summary.visual_blockers.push('SCREENSHOT_MISSING_OR_EMPTY:MOBILE_390x844')
  addVisualReq('MOBILE_SCREENSHOT_PRESENT', mobileOk, 'SCREENSHOT_MISSING_OR_EMPTY:MOBILE_390x844')
  addVisualReq('MOBILE_OWNER_OR_RESPONSIVE_UI', hasOwner(mobileText) || /SYSTEM3|AI OPTIONS CONTROL/i.test(mobileText), 'OWNER_BADGE_NOT_VISIBLE:MOBILE_OR_RESPONSIVE_UI')
} finally {
  await browser.close()
}

summary.visual_blockers = Array.from(new Set(summary.visual_blockers))
summary.infra_blockers = Array.from(new Set(summary.infra_blockers))
summary.trade_readiness_blockers = Array.from(new Set(summary.trade_readiness_blockers))
summary.blockers = [...summary.infra_blockers, ...summary.trade_readiness_blockers, ...summary.visual_blockers]
summary.solutions = summary.blockers.map(b => ({ blocker: b, solution: solutionFor(b) }))
summary.final_verdict = summary.infra_blockers.length || summary.visual_blockers.length ? 'FAIL' : (summary.trade_readiness_blockers.length ? 'BLOCKED_NOT_TRADE_READY' : 'PASS')
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Dashboard Live UI Proof', '', `Generated: ${summary.generated_at}`, `Base: ${summary.base}`, `Required symbols: ${summary.required_symbols.join(', ')}`, `Optional symbols: ${summary.optional_symbols.join(', ') || '-'}`, `Final verdict: **${summary.final_verdict}**`, `Owner badge visible: **${summary.owner_badge_visible}**`, `Safety labels visible: **${summary.safety_labels_visible}**`, `ML proof visible: **${summary.ml_proof_visible}**`, `Paper truth visible: **${summary.paper_truth_visible}**`, `Trader readiness panel visible: **${summary.trader_readiness_panel_visible}**`, `Truth control visible: **${summary.truth_control_visible}**`, '',
  '## Visual Requirements', ...summary.visual_requirements.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.id}${x.blocker ? ` blocker=${x.blocker}` : ''}`), '',
  '## Chain Truth', ...summary.chain_truth.map(x => `- ${x.ok ? 'PASS' : (x.safe_blocked ? 'BLOCKED' : 'FAIL')} ${x.optional ? '(optional)' : '(required)'} ${x.endpoint} source=${x.source} priority=${x.source_priority} status=${x.status} spot=${x.spot} contracts=${x.total_contracts} blocker=${x.blocker || '-'}`), '',
  '## API', ...summary.api.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.status} ${x.optional ? '(optional)' : ''} ${x.endpoint}`), '',
  '## UI Screenshots', ...summary.ui.map(x => `- ${x.ok ? 'PASS' : 'FAIL'} ${x.title} owner=${x.owner_visible} safety=${x.safety_labels_visible} ml=${x.ml_proof_visible} paper=${x.paper_truth_visible}${x.error ? ` - ${x.error}` : ''}`), '',
  '## Infrastructure Blockers', ...(summary.infra_blockers.length ? summary.infra_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Visual Blockers', ...(summary.visual_blockers.length ? summary.visual_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Trading Readiness Blockers', ...(summary.trade_readiness_blockers.length ? summary.trade_readiness_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Optional Data Blockers', ...(summary.optional_data_blockers.length ? summary.optional_data_blockers.map(x => `- ${x}`) : ['- none']), '',
  '## Required Solutions', ...(summary.solutions.length ? summary.solutions.map(x => `- ${x.blocker}: ${x.solution}`) : ['- none'])
].join('\n'))

if (summary.infra_blockers.length || summary.visual_blockers.length) { console.error(`DASHBOARD_LIVE_UI_PROOF_FAILED infra_blockers=${summary.infra_blockers.length} visual_blockers=${summary.visual_blockers.length}`); console.error([...summary.infra_blockers, ...summary.visual_blockers].join('\n')); process.exit(1) }
if (summary.trade_readiness_blockers.length) { console.error(`DASHBOARD_LIVE_UI_PROOF_BLOCKED_NOT_TRADE_READY trade_blockers=${summary.trade_readiness_blockers.length}`); console.error(summary.trade_readiness_blockers.join('\n')) }
