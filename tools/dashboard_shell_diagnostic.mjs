import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const outDir = path.join('reports', 'latest', 'dashboard_shell_diagnostic')
fs.mkdirSync(outDir, { recursive: true })

const fallbackExpectedTabs = [
  'Truth Control', 'Genesis Brain', 'E2E Proof', 'Overview', 'Sim Live',
  'Option Chain', 'Signals', 'Trade', 'Paper Trades', 'Positions',
  'Performance', 'ML Model', 'Broker', 'Alerts', 'System', 'Live Gate',
]

function sourceExpectedTabs() {
  const sidebarPath = path.join('dashboard', 'frontend', 'src', 'components', 'Sidebar.tsx')
  try {
    const source = fs.readFileSync(sidebarPath, 'utf8')
    const labels = [...source.matchAll(/label:\s*['"]([^'"]+)['"]/g)].map(match => match[1].trim())
    return [...new Set(labels.filter(Boolean))]
  } catch {
    return fallbackExpectedTabs
  }
}

const expectedTabs = sourceExpectedTabs()
const safeText = value => String(value || '').replace(/\s+/g, ' ').trim().slice(0, 240)
const summary = {
  generated_at: new Date().toISOString(),
  base,
  status: 'BLOCKED',
  analyzer_mode: true,
  live_trading_enabled: false,
  order_routes_called: false,
  secrets_persisted: false,
  auth: { ok: false, status: 0 },
  ui_response_status: 0,
  render_ui_available: false,
  availability_attempts: [],
  recovered_after_transient_failure: false,
  final_url: '',
  page_title: '',
  body_text_length: 0,
  root_child_count: 0,
  visible_button_count: 0,
  visible_link_count: 0,
  expected_tab_count: expectedTabs.length,
  expected_tabs_source: 'dashboard/frontend/src/components/Sidebar.tsx',
  matched_tab_count: 0,
  matched_tabs: [],
  missing_tabs: [],
  deployed_asset_drift_detected: false,
  safe_visible_controls: [],
  console_error_types: [],
  page_error_types: [],
  blocker: 'NOT_RUN',
  production_grade_claim_allowed: false,
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

async function gotoWithRecovery(page, url) {
  const maxAttempts = Math.max(1, Math.min(4, Number(process.env.DASHBOARD_UI_MAX_ATTEMPTS || 3)))
  const retryDelayMs = Math.max(1000, Math.min(30000, Number(process.env.DASHBOARD_UI_RETRY_DELAY_MS || 12000)))
  let response = null

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    let status = 0
    let errorType = ''
    try {
      response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 })
      status = response?.status() || 0
    } catch (err) {
      errorType = err?.name || 'NavigationError'
    }

    summary.availability_attempts.push({ attempt, status, error_type: errorType })
    if (status >= 200 && status < 400) {
      summary.recovered_after_transient_failure = attempt > 1
      return response
    }
    if (attempt < maxAttempts) await sleep(retryDelayMs)
  }
  return response
}

let browser
try {
  browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 },
    extraHTTPHeaders: key ? { 'X-API-Key': key } : {},
  })
  const page = await context.newPage()
  page.on('console', msg => {
    if (msg.type() === 'error') summary.console_error_types.push('console.error')
  })
  page.on('pageerror', err => {
    summary.page_error_types.push(err?.name || 'PageError')
  })

  const first = await gotoWithRecovery(page, `${base}/ui/`)
  summary.ui_response_status = first?.status() || summary.availability_attempts.at(-1)?.status || 0
  summary.render_ui_available = summary.ui_response_status >= 200 && summary.ui_response_status < 400

  if (key && summary.render_ui_available) {
    summary.auth = await page.evaluate(async apiKey => {
      const response = await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
        credentials: 'include',
        body: JSON.stringify({ api_key: apiKey }),
      })
      return { ok: response.ok, status: response.status }
    }, key).catch(() => ({ ok: false, status: 0 }))
  }

  if (summary.render_ui_available) {
    await page.reload({ waitUntil: 'networkidle', timeout: 90000 }).catch(() => null)
    await page.waitForTimeout(8000)
  }

  const shell = await page.evaluate(expected => {
    const visible = el => {
      const style = getComputedStyle(el)
      const rect = el.getBoundingClientRect()
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0
    }
    const controls = [...document.querySelectorAll('button,a')]
      .filter(visible)
      .map(el => (el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || '').replace(/\s+/g, ' ').trim())
      .filter(Boolean)
    const matched = expected.filter(title => controls.some(text => text === title || text.includes(title)))
    return {
      finalUrl: location.href,
      title: document.title,
      bodyLength: (document.body?.innerText || '').length,
      rootChildCount: document.querySelector('#root')?.childElementCount || 0,
      buttonCount: [...document.querySelectorAll('button')].filter(visible).length,
      linkCount: [...document.querySelectorAll('a')].filter(visible).length,
      controls: [...new Set(controls)].slice(0, 40),
      matched,
    }
  }, expectedTabs)

  summary.final_url = safeText(shell.finalUrl)
  summary.page_title = safeText(shell.title)
  summary.body_text_length = shell.bodyLength
  summary.root_child_count = shell.rootChildCount
  summary.visible_button_count = shell.buttonCount
  summary.visible_link_count = shell.linkCount
  summary.safe_visible_controls = shell.controls.map(safeText)
  summary.matched_tabs = shell.matched
  summary.matched_tab_count = shell.matched.length
  summary.missing_tabs = summary.render_ui_available
    ? expectedTabs.filter(title => !shell.matched.includes(title))
    : []
  summary.deployed_asset_drift_detected = summary.render_ui_available && summary.missing_tabs.length > 0
  summary.console_error_types = [...new Set(summary.console_error_types)]
  summary.page_error_types = [...new Set(summary.page_error_types)]

  if (!summary.render_ui_available) summary.blocker = 'RENDER_UI_UNAVAILABLE_AFTER_RETRIES'
  else if (!summary.auth.ok) summary.blocker = 'DASHBOARD_AUTH_NOT_PROVEN'
  else if (summary.root_child_count === 0 || summary.body_text_length === 0) summary.blocker = 'FRONTEND_ROOT_EMPTY'
  else if (summary.missing_tabs.length) summary.blocker = 'DEPLOYED_FRONTEND_ASSET_DRIFT'
  else if (summary.page_error_types.length || summary.console_error_types.length) summary.blocker = 'FRONTEND_RUNTIME_ERRORS_PRESENT'
  else {
    summary.status = 'PASS'
    summary.blocker = 'NONE'
  }
} catch (err) {
  summary.blocker = err?.name === 'TimeoutError' ? 'DASHBOARD_SHELL_TIMEOUT' : 'DASHBOARD_SHELL_EXCEPTION'
  summary.page_error_types = [...new Set([...summary.page_error_types, err?.name || 'Error'])]
} finally {
  if (browser) await browser.close().catch(() => {})
}

summary.production_grade_claim_allowed = false
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))
fs.writeFileSync(path.join(outDir, 'summary.md'), [
  '# Dashboard Shell Diagnostic',
  '',
  `Generated: ${summary.generated_at}`,
  `Status: **${summary.status}**`,
  `Blocker: **${summary.blocker}**`,
  `Render UI available: \`${summary.render_ui_available}\``,
  `Availability attempts: \`${summary.availability_attempts.map(item => `${item.attempt}:${item.status || item.error_type || 'error'}`).join(', ') || 'none'}\``,
  `Recovered after transient failure: \`${summary.recovered_after_transient_failure}\``,
  `Auth OK: \`${summary.auth.ok}\` (HTTP ${summary.auth.status})`,
  `UI HTTP: \`${summary.ui_response_status}\``,
  `Root children: \`${summary.root_child_count}\``,
  `Body text length: \`${summary.body_text_length}\``,
  `Matched tabs: \`${summary.matched_tab_count}/${summary.expected_tab_count}\``,
  `Missing source-defined tabs: \`${summary.missing_tabs.join(', ') || 'not evaluated / none'}\``,
  `Deployed asset drift: \`${summary.deployed_asset_drift_detected}\``,
  `Visible buttons: \`${summary.visible_button_count}\``,
  `Visible links: \`${summary.visible_link_count}\``,
  `Console error categories: \`${summary.console_error_types.join(', ') || 'none'}\``,
  `Page error categories: \`${summary.page_error_types.join(', ') || 'none'}\``,
  '',
  'This report is analyzer-only. It never calls order routes, never persists credentials, and never permits a production-grade claim.',
].join('\n'))

console.log(JSON.stringify({
  status: summary.status,
  blocker: summary.blocker,
  render_ui_available: summary.render_ui_available,
  availability_attempts: summary.availability_attempts,
  recovered_after_transient_failure: summary.recovered_after_transient_failure,
  auth_ok: summary.auth.ok,
  ui_http: summary.ui_response_status,
  matched_tabs: `${summary.matched_tab_count}/${summary.expected_tab_count}`,
  missing_tabs: summary.missing_tabs,
  deployed_asset_drift_detected: summary.deployed_asset_drift_detected,
  live_trading_enabled: false,
  order_routes_called: false,
}))