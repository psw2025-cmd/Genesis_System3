import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
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
  '0/4', '0 / 4', 'MISSING', 'STALE', 'TIMEOUT',
  'INVALID', 'EXPIRED', 'UNAVAILABLE', 'UNHEALTHY', 'DEGRADED', 'AUTH REQUIRED',
]

const informativeWords = ['NO TRADE', 'NO SIGNAL', 'MARKET CLOSED', 'LIVE OFF', 'PAPER']
const loadingMarkers = [
  'CHECKING...',
  'CHECKING MODEL ARTIFACTS...',
  'GENESIS IS LOADING PRODUCTION COMMAND INTELLIGENCE...',
  'LOADING...',
]
const settleTimeoutMs = Math.min(Math.max(Number(process.env.DASHBOARD_TAB_SETTLE_TIMEOUT_MS || 20000), 5000), 60000)
const settlePollMs = 1000

function uniq(items) {
  return Array.from(new Set(items.filter(Boolean)))
}

function isAllowedSafetyLine(text) {
  const t = String(text || '').toUpperCase().replace(/\s+/g, ' ').trim()
  const liveTradingSafety = t.includes('LIVE TRADING') && (
    t.includes('OFF') ||
    t.includes('DISABLED') ||
    t.includes('BLOCKED BY BACKEND FLAG') ||
    t.includes('NOT ALLOWED')
  )
  const orderSafety = t.includes('ORDER') && (
    t.includes('NOT CALLED') ||
    t.includes('PLACEMENT DISABLED') ||
    t.includes('EXECUTION DISABLED')
  )
  return liveTradingSafety || orderSafety
}

function classifyLine(line) {
  const t = String(line || '').toUpperCase()
  if (!t.trim()) return null
  if (isAllowedSafetyLine(t)) return null
  if (blockerWords.some(w => t.includes(w))) return { severity: 'BLOCKER', text: line }
  if (informativeWords.some(w => t.includes(w))) return { severity: 'INFO', text: line }
  return null
}

async function authenticate(page, summary) {
  if (!key) {
    summary.todo.push('DASHBOARD_API_KEY missing in workflow env; UI may show locked/auth state instead of real dashboard proof')
    return { ok: false, status: 0, note: 'DASHBOARD_API_KEY missing' }
  }
  try {
    const auth = await page.evaluate(async (apiKey) => {
      const r = await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
        credentials: 'include',
        body: JSON.stringify({ api_key: apiKey }),
      })
      return { ok: r.ok, status: r.status }
    }, key)
    if (!auth.ok) summary.todo.push(`Dashboard auth session failed status=${auth.status}`)
    return auth
  } catch (err) {
    summary.todo.push(`Dashboard auth session exception: ${String(err).slice(0, 300)}`)
    return { ok: false, status: 0, error: String(err) }
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
      if (stableReads >= 2) {
        return { settled: true, elapsed_ms: Date.now() - startedAt, remaining_markers: [] }
      }
    } else {
      stableReads = 0
    }

    previousText = normalized
    await page.waitForTimeout(settlePollMs)
  }

  return {
    settled: false,
    elapsed_ms: Date.now() - startedAt,
    remaining_markers: uniq(lastMarkers),
  }
}

async function scanTab(page, id, title) {
  const result = {
    id,
    title,
    ok: false,
    screenshot: null,
    screenshot_ok: false,
    navigation_method_index: null,
    async_content_settled: false,
    settle_elapsed_ms: 0,
    settle_remaining_markers: [],
    blocker_lines: [],
    info_lines: [],
    red_elements: [],
    ui_exceptions: [],
    body_text_sample: '',
  }

  try {
    const navigation = await clickDashboardTab(page, title)
    result.navigation_method_index = navigation.method_index
    const settle = await waitForTabToSettle(page)
    result.async_content_settled = settle.settled
    result.settle_elapsed_ms = settle.elapsed_ms
    result.settle_remaining_markers = settle.remaining_markers
    if (!settle.settled) {
      const markerText = settle.remaining_markers.length ? ` markers=${settle.remaining_markers.join('|')}` : ''
      result.blocker_lines.push(`ASYNC_CONTENT_NOT_SETTLED after ${settle.elapsed_ms}ms${markerText}`)
    }

    const screenshot = path.join(outDir, `${id}.png`)
    await page.screenshot({ path: screenshot, fullPage: true })
    result.screenshot = screenshot
    result.screenshot_ok = fs.existsSync(screenshot) && fs.statSync(screenshot).size > 10000

    const text = await page.locator('body').innerText({ timeout: 15000 }).catch(() => '')
    result.body_text_sample = String(text).slice(0, 6000)
    fs.writeFileSync(path.join(outDir, `${id}.txt`), result.body_text_sample)
    const lines = uniq(String(text).split('\n').map(x => x.trim()).filter(x => x.length > 1))
    for (const line of lines) {
      const hit = classifyLine(line)
      if (!hit) continue
      if (hit.severity === 'BLOCKER') result.blocker_lines.push(hit.text)
      if (hit.severity === 'INFO') result.info_lines.push(hit.text)
    }

    result.red_elements = await page.evaluate(() => {
      const out = []
      const nodes = Array.from(document.querySelectorAll('body *'))
      for (const el of nodes) {
        const text = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ')
        if (!text || text.length < 2 || text.length > 220) continue
        const cls = String(el.className || '')
        const cs = window.getComputedStyle(el)
        const color = cs.color || ''
        const bg = cs.backgroundColor || ''
        const redClass = /tx-down|text-red|bg-red|border-red|danger|error|fail|blocked/i.test(cls)
        const redColor = /rgb\((?:2[0-5][0-5]|1[6-9][0-9]),\s*(?:0|[1-9][0-9]),\s*(?:0|[1-9][0-9])\)/i.test(color)
        const amberClass = /text-yellow|bg-yellow|text-amber|bg-amber|warning|pending/i.test(cls)
        if (redClass || redColor || amberClass) out.push({ text, className: cls.slice(0, 160), color, backgroundColor: bg })
        if (out.length >= 120) break
      }
      return out
    })

    for (const el of result.red_elements) {
      const hit = classifyLine(el.text)
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
  generated_at: new Date().toISOString(),
  base,
  status: 'UNKNOWN',
  auth: null,
  tabs: [],
  expected_tab_count: tabs.length,
  visible_issue_count: 0,
  info_line_count: 0,
  screenshot_missing_count: 0,
  unsettled_tab_count: 0,
  ui_exception_count: 0,
  global_exception: null,
  visible_issues: [],
  info_lines: [],
  todo: [],
  production_grade_claim_allowed: false,
  analyzer_safety: {
    analyze_mode: process.env.ANALYZE_MODE === '1',
    live_trading_enabled: process.env.LIVE_TRADING_ENABLED === '1',
    system3_live_trading_allowed: process.env.SYSTEM3_LIVE_TRADING_ALLOWED === '1',
  },
}

let browser = null
try {
  browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ viewport: { width: 1366, height: 768 }, extraHTTPHeaders: key ? { 'X-API-Key': key } : {} })
  const page = await context.newPage()

  try {
    await page.goto(`${base}/ui/`, { waitUntil: 'domcontentloaded', timeout: 90000 })
    await page.waitForTimeout(4000)
    try {
      await page.screenshot({ path: path.join(outDir, 'landing.png'), fullPage: true })
    } catch {}
    summary.auth = await authenticate(page, summary)
    await page.goto(`${base}/ui/`, { waitUntil: 'domcontentloaded', timeout: 90000 })
    await page.waitForTimeout(5000)

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
      for (const line of r.info_lines) {
        summary.info_lines.push({ tab: title, text: line })
      }
    }
  } catch (err) {
    summary.global_exception = String(err).slice(0, 1000)
    summary.todo.push(`Live dashboard UI scan failed before tab scan: ${summary.global_exception}`)
  }
} catch (err) {
  summary.global_exception = String(err).slice(0, 1000)
  summary.todo.push(`Playwright/browser launch failed: ${summary.global_exception}`)
} finally {
  if (browser) await browser.close().catch(() => {})
}

summary.visible_issues = summary.visible_issues.slice(0, 500)
summary.info_lines = summary.info_lines.slice(0, 300)
summary.todo = uniq(summary.todo).slice(0, 500)
summary.visible_issue_count = summary.visible_issues.length
summary.info_line_count = summary.info_lines.length
summary.status = summary.tabs.length !== tabs.length || summary.visible_issue_count || summary.screenshot_missing_count || summary.unsettled_tab_count || summary.ui_exception_count || summary.global_exception || !summary.auth?.ok ? 'BLOCKED' : 'PASS'
summary.production_grade_claim_allowed = summary.status === 'PASS'

fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))

const md = [
  '# Dashboard Visible Issue Tracker',
  '',
  `Generated: ${summary.generated_at}`,
  `Base: ${summary.base}`,
  `Status: **${summary.status}**`,
  `Expected tab count: \`${summary.expected_tab_count}\``,
  `Scanned tab count: \`${summary.tabs.length}\``,
  `Visible blocker count: \`${summary.visible_issue_count}\``,
  `Info line count: \`${summary.info_line_count}\``,
  `Screenshot missing count: \`${summary.screenshot_missing_count}\``,
  `Unsettled tab count: \`${summary.unsettled_tab_count}\``,
  `UI exception count: \`${summary.ui_exception_count}\``,
  `Auth OK: \`${Boolean(summary.auth?.ok)}\``,
  `Production-grade claim allowed: \`${summary.production_grade_claim_allowed}\``,
  summary.global_exception ? `Global exception: \`${summary.global_exception}\`` : '',
  '',
  '## Rule',
  '',
  'Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.',
  '',
  '## TODO',
  '',
  ...(summary.todo.length ? summary.todo.map(x => `- [ ] ${x}`) : ['- [x] No visible UI blockers detected.']),
  '',
  '## Tab results',
  '',
  '| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |',
  '|---|---|---:|---:|---:|---:|---:|---:|---|',
  ...summary.tabs.map(t => `| ${t.title} | ${t.ok ? 'PASS' : 'BLOCKED'} | ${t.screenshot_ok ? 'OK' : 'MISSING'} | ${t.async_content_settled ? 'YES' : 'NO'} | ${t.settle_elapsed_ms} | ${t.blocker_lines.length} | ${t.info_lines.length} | ${t.ui_exceptions.length} | ${t.id}.txt |`),
  '',
  '## Visible blockers',
  '',
  ...(summary.visible_issues.length ? summary.visible_issues.map(x => `- **${x.tab}**: ${x.text}`) : ['- none']),
  '',
  '## Informational lines',
  '',
  ...(summary.info_lines.length ? summary.info_lines.slice(0, 120).map(x => `- **${x.tab}**: ${x.text}`) : ['- none']),
].filter(Boolean).join('\n')

fs.writeFileSync(path.join(outDir, 'summary.md'), md + '\n')

if (summary.status !== 'PASS') {
  console.error(`DASHBOARD_VISIBLE_ISSUES_BLOCKED issues=${summary.visible_issue_count} screenshots_missing=${summary.screenshot_missing_count} unsettled_tabs=${summary.unsettled_tab_count} exceptions=${summary.ui_exception_count} auth_ok=${Boolean(summary.auth?.ok)} tabs=${summary.tabs.length}/${tabs.length}`)
  process.exit(1)
}
