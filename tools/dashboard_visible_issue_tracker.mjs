import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
const outDir = path.join('reports', 'latest', 'dashboard_visible_issue_tracker')
fs.mkdirSync(outDir, { recursive: true })

const tabs = [
  ['truth', 'Truth Control'],
  ['genesis', 'Genesis Brain'],
  ['e2e_proof', 'E2E Proof'],
  ['overview', 'Overview'],
  ['sim_live', 'Sim Live'],
  ['chain', 'Option Chain'],
  ['signals', 'Signals'],
  ['trade', 'Trade'],
  ['paper', 'Paper Trades'],
  ['positions', 'Positions'],
  ['performance', 'Performance'],
  ['ml', 'ML Model'],
  ['broker', 'Broker'],
  ['alerts', 'Alerts'],
  ['system', 'System'],
  ['gates', 'Live Gate'],
]

const blockerWords = [
  'ERROR', 'FAIL', 'FAILED', 'BLOCKED', 'PEND', 'PENDING', 'NOT READY', 'NOT PROVEN',
  '0/4', '0 / 4', 'MISSING', 'STALE', 'TIMEOUT', 'INVALID', 'EXPIRED', 'UNAVAILABLE',
  'UNHEALTHY', 'DEGRADED', 'AUTH REQUIRED',
]
const informativeWords = ['NO TRADE', 'NO SIGNAL', 'MARKET CLOSED', 'LIVE OFF', 'PAPER']
const loadingMarkers = ['CHECKING...', 'CHECKING MODEL ARTIFACTS...', 'GENESIS IS LOADING PRODUCTION COMMAND INTELLIGENCE...', 'LOADING...']
const settleTimeoutMs = Math.min(Math.max(Number(process.env.DASHBOARD_TAB_SETTLE_TIMEOUT_MS || 20000), 5000), 60000)
const settlePollMs = 1000

function uniq(items) { return Array.from(new Set(items.filter(Boolean))) }
function isAllowedSafetyLine(text) {
  const t = String(text || '').toUpperCase().replace(/\s+/g, ' ').trim()
  const liveSafety = t.includes('LIVE TRADING') && (t.includes('OFF') || t.includes('DISABLED') || t.includes('BLOCKED BY BACKEND FLAG') || t.includes('NOT ALLOWED'))
  const orderSafety = t.includes('ORDER') && (t.includes('NOT CALLED') || t.includes('PLACEMENT DISABLED') || t.includes('EXECUTION DISABLED'))
  return liveSafety || orderSafety
}
function classifyLine(line) {
  const t = String(line || '').toUpperCase()
  if (!t.trim() || isAllowedSafetyLine(t)) return null
  if (blockerWords.some(w => t.includes(w))) return { severity: 'BLOCKER', text: line }
  if (informativeWords.some(w => t.includes(w))) return { severity: 'INFO', text: line }
  return null
}

async function getJson(page, endpoint) {
  return page.evaluate(async (pathName) => {
    const response = await fetch(pathName, { method: 'GET', credentials: 'omit', cache: 'no-store' })
    let payload = null
    try { payload = await response.json() } catch {}
    return { ok: response.ok, status: response.status, payload }
  }, endpoint)
}

async function provePublicReadonly(page) {
  const auth = await getJson(page, '/api/auth/status')
  const payload = auth.payload || {}
  return {
    ok: auth.ok && auth.status === 200 && payload.required === false && payload.configured === false &&
      payload.authenticated === false && payload.mode === 'public_readonly' &&
      payload.credential_surface === 'REMOVED' && payload.session === null,
    status: auth.status,
    mode: payload.mode || null,
    required: payload.required,
    configured: payload.configured,
    authenticated: payload.authenticated,
    credential_surface: payload.credential_surface || null,
    session_is_null: payload.session === null,
  }
}

async function clickDashboardTab(page, title) {
  const candidates = [
    page.getByRole('button', { name: title, exact: true }),
    page.getByRole('link', { name: title, exact: true }),
    page.locator('button').filter({ hasText: title }),
    page.locator('a').filter({ hasText: title }),
    page.locator(`[title=${JSON.stringify(title)}]`),
    page.locator(`[aria-label=${JSON.stringify(title)}]`),
    page.getByText(title, { exact: true }),
  ]
  const attempts = []
  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = candidates[index].first()
    try {
      await candidate.waitFor({ state: 'visible', timeout: 3000 })
      await candidate.click({ timeout: 8000 })
      return { method_index: index, attempts }
    } catch (err) {
      attempts.push(`candidate_${index}:${String(err).split('\n')[0].slice(0, 180)}`)
    }
  }
  throw new Error(`Unable to locate/click dashboard tab ${title}; ${attempts.join(' | ')}`)
}

async function waitForTabToSettle(page) {
  const startedAt = Date.now()
  let lastMarkers = []
  let stableReads = 0
  let previousText = ''
  while (Date.now() - startedAt < settleTimeoutMs) {
    const bodyText = await page.locator('body').innerText({ timeout: 5000 }).catch(() => '')
    const normalized = String(bodyText).toUpperCase().replace(/\s+/g, ' ').trim()
    lastMarkers = loadingMarkers.filter(marker => normalized.includes(marker))
    if (lastMarkers.length === 0 && normalized && normalized === previousText) {
      stableReads += 1
      if (stableReads >= 2) return { settled: true, elapsed_ms: Date.now() - startedAt, remaining_markers: [] }
    } else {
      stableReads = 0
    }
    previousText = normalized
    await page.waitForTimeout(settlePollMs)
  }
  return { settled: false, elapsed_ms: Date.now() - startedAt, remaining_markers: uniq(lastMarkers) }
}

async function scanTab(page, id, title) {
  const result = {
    id, title, ok: false, screenshot: null, screenshot_ok: false, navigation_method_index: null,
    async_content_settled: false, settle_elapsed_ms: 0, settle_remaining_markers: [], blocker_lines: [],
    info_lines: [], ui_exceptions: [], body_text_sample: '',
  }
  try {
    const navigation = await clickDashboardTab(page, title)
    result.navigation_method_index = navigation.method_index
    const settle = await waitForTabToSettle(page)
    result.async_content_settled = settle.settled
    result.settle_elapsed_ms = settle.elapsed_ms
    result.settle_remaining_markers = settle.remaining_markers
    if (!settle.settled) result.blocker_lines.push(`ASYNC_CONTENT_NOT_SETTLED after ${settle.elapsed_ms}ms`)

    const screenshot = path.join(outDir, `${id}.png`)
    await page.screenshot({ path: screenshot, fullPage: true })
    result.screenshot = screenshot
    result.screenshot_ok = fs.existsSync(screenshot) && fs.statSync(screenshot).size > 10000

    const text = await page.locator('body').innerText({ timeout: 15000 }).catch(() => '')
    result.body_text_sample = String(text).slice(0, 6000)
    fs.writeFileSync(path.join(outDir, `${id}.txt`), result.body_text_sample)
    for (const line of uniq(String(text).split('\n').map(x => x.trim()).filter(x => x.length > 1))) {
      const hit = classifyLine(line)
      if (!hit) continue
      if (hit.severity === 'BLOCKER') result.blocker_lines.push(hit.text)
      if (hit.severity === 'INFO') result.info_lines.push(hit.text)
    }
    result.blocker_lines = uniq(result.blocker_lines).slice(0, 150)
    result.info_lines = uniq(result.info_lines).slice(0, 100)
    result.ok = result.screenshot_ok && result.async_content_settled && result.blocker_lines.length === 0
  } catch (err) {
    result.ui_exceptions.push(String(err).slice(0, 500))
  }
  return result
}

const summary = {
  generated_at: new Date().toISOString(), base, status: 'UNKNOWN', public_readonly: null,
  health: null, broker: null, tabs: [], expected_tab_count: tabs.length, visible_issue_count: 0,
  info_line_count: 0, screenshot_missing_count: 0, unsettled_tab_count: 0, ui_exception_count: 0,
  global_exception: null, visible_issues: [], info_lines: [], todo: [], production_grade_claim_allowed: false,
  browser_credentials_sent: false, browser_mutations_called: false, order_endpoints_called: false,
  analyzer_safety: {
    analyze_mode: process.env.ANALYZE_MODE === '1',
    live_trading_enabled: process.env.LIVE_TRADING_ENABLED === '1',
    system3_live_trading_allowed: process.env.SYSTEM3_LIVE_TRADING_ALLOWED === '1',
  },
}

let browser = null
try {
  browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ viewport: { width: 1366, height: 768 } })
  const page = await context.newPage()
  await page.goto(`${base}/ui/`, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.waitForTimeout(4000)
  summary.public_readonly = await provePublicReadonly(page)
  summary.health = await getJson(page, '/api/health')
  summary.broker = await getJson(page, '/api/broker/status')
  if (!summary.public_readonly.ok) summary.todo.push('Public-readonly auth contract drift')
  if (!summary.health.ok) summary.todo.push(`Health sentinel failed HTTP ${summary.health.status}`)
  if (!summary.broker.ok) summary.todo.push(`Broker sentinel failed HTTP ${summary.broker.status}`)

  try { await page.screenshot({ path: path.join(outDir, 'landing.png'), fullPage: true }) } catch {}
  for (const [id, title] of tabs) {
    const r = await scanTab(page, id, title)
    summary.tabs.push(r)
    if (!r.screenshot_ok) summary.screenshot_missing_count += 1
    if (!r.async_content_settled) summary.unsettled_tab_count += 1
    summary.ui_exception_count += r.ui_exceptions.length
    for (const line of r.blocker_lines) {
      summary.visible_issues.push({ tab: title, text: line })
      summary.todo.push(`Fix visible UI blocker on ${title}: ${line}`)
    }
    for (const line of r.info_lines) summary.info_lines.push({ tab: title, text: line })
  }
} catch (err) {
  summary.global_exception = String(err).slice(0, 1000)
  summary.todo.push(`Live dashboard UI scan failed: ${summary.global_exception}`)
} finally {
  if (browser) await browser.close().catch(() => {})
}

summary.visible_issues = summary.visible_issues.slice(0, 500)
summary.info_lines = summary.info_lines.slice(0, 300)
summary.todo = uniq(summary.todo).slice(0, 500)
summary.visible_issue_count = summary.visible_issues.length
summary.info_line_count = summary.info_lines.length
summary.status = summary.tabs.length !== tabs.length || summary.visible_issue_count || summary.screenshot_missing_count ||
  summary.unsettled_tab_count || summary.ui_exception_count || summary.global_exception || !summary.public_readonly?.ok ||
  !summary.health?.ok || !summary.broker?.ok ? 'BLOCKED' : 'PASS'
summary.production_grade_claim_allowed = summary.status === 'PASS'

fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
const md = [
  '# Dashboard Visible Issue Tracker', '', `Generated: ${summary.generated_at}`, `Base: ${summary.base}`,
  `Status: **${summary.status}**`, `Expected tab count: \`${summary.expected_tab_count}\``,
  `Scanned tab count: \`${summary.tabs.length}\``, `Visible blocker count: \`${summary.visible_issue_count}\``,
  `Screenshot missing count: \`${summary.screenshot_missing_count}\``, `Unsettled tab count: \`${summary.unsettled_tab_count}\``,
  `UI exception count: \`${summary.ui_exception_count}\``, `Public-readonly contract: \`${Boolean(summary.public_readonly?.ok)}\``,
  `Health HTTP: \`${summary.health?.status ?? 0}\``, `Broker HTTP: \`${summary.broker?.status ?? 0}\``,
  `Browser credentials sent: \`${summary.browser_credentials_sent}\``, `Browser mutations called: \`${summary.browser_mutations_called}\``,
  `Order endpoints called: \`${summary.order_endpoints_called}\``, `Production-grade claim allowed: \`${summary.production_grade_claim_allowed}\``,
  '', '## Rule', '', 'All dashboard reads are anonymous/public-readonly. Health and broker sentinels are mandatory. No credential, session, mutation, or order endpoint may be used.',
  '', '## TODO', ...summary.todo.map(x => `- ${x}`), '', '## Tabs',
  ...summary.tabs.map(t => `- ${t.title}: ${t.ok ? 'PASS' : 'BLOCKED'}; screenshot=${t.screenshot_ok}; settled=${t.async_content_settled}; blockers=${t.blocker_lines.length}; exceptions=${t.ui_exceptions.length}`),
].join('\n')
fs.writeFileSync(path.join(outDir, 'summary.md'), md)

if (summary.status === 'PASS') {
  console.log(`DASHBOARD_VISIBLE_ISSUES_PASS tabs=${summary.tabs.length}/${tabs.length} screenshots=${tabs.length - summary.screenshot_missing_count}/${tabs.length}`)
  process.exit(0)
}
console.error(`DASHBOARD_VISIBLE_ISSUES_BLOCKED issues=${summary.visible_issue_count} screenshots_missing=${summary.screenshot_missing_count} unsettled_tabs=${summary.unsettled_tab_count} exceptions=${summary.ui_exception_count} public_readonly=${Boolean(summary.public_readonly?.ok)} health=${summary.health?.status ?? 0} broker=${summary.broker?.status ?? 0} tabs=${summary.tabs.length}/${tabs.length}`)
process.exit(1)
