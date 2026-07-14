import { chromium } from 'playwright'

const base = (process.env.DASHBOARD_BASE_URL || 'https://genesis-system3-backend.onrender.com').replace(/\/+$/, '')
const key = process.env.DASHBOARD_API_KEY || ''
const attempts = Math.min(Math.max(Number(process.env.DASHBOARD_WARMUP_ATTEMPTS || 3), 1), 5)
const waitMs = Math.min(Math.max(Number(process.env.DASHBOARD_WARMUP_WAIT_MS || 12000), 2000), 30000)

if (!key) {
  console.error('DASHBOARD_SHELL_WARMUP_BLOCKED reason=missing_dashboard_api_key')
  process.exit(1)
}

let browser
const sanitizedAttempts = []
try {
  browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 },
    extraHTTPHeaders: { 'X-API-Key': key },
  })
  const page = await context.newPage()

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    let uiStatus = 0
    let authStatus = 0
    let dashboardRendered = false
    let tabCount = 0
    try {
      const response = await page.goto(`${base}/ui/`, { waitUntil: 'domcontentloaded', timeout: 90000 })
      uiStatus = response?.status() || 0
      const auth = await page.evaluate(async (apiKey) => {
        const response = await fetch('/api/auth/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
          credentials: 'include',
          body: JSON.stringify({ api_key: apiKey }),
        })
        return { ok: response.ok, status: response.status }
      }, key)
      authStatus = auth.status
      if (auth.ok) {
        await page.goto(`${base}/ui/`, { waitUntil: 'domcontentloaded', timeout: 90000 })
        await page.waitForFunction(() => {
          const body = (document.body?.innerText || '').trim()
          const nav = document.querySelector('[data-dashboard-navigation="sidebar"]')
          const tabs = document.querySelectorAll('[data-dashboard-tab]')
          return Boolean(body && (nav || tabs.length > 0))
        }, { timeout: waitMs })
        dashboardRendered = true
        tabCount = await page.locator('[data-dashboard-tab]').count()
      }
    } catch {
      // Persist only sanitized status metadata; never persist response bodies or credentials.
    }

    sanitizedAttempts.push({ attempt, ui_status: uiStatus, auth_status: authStatus, dashboard_rendered: dashboardRendered, tab_count: tabCount })
    if (uiStatus === 200 && authStatus === 200 && dashboardRendered) {
      console.log(JSON.stringify({ status: 'PASS', recovered_on_attempt: attempt, tab_count: tabCount, attempts: sanitizedAttempts }))
      process.exit(0)
    }
    if (attempt < attempts) await page.waitForTimeout(waitMs)
  }

  console.error(`DASHBOARD_SHELL_WARMUP_BLOCKED ${JSON.stringify({ status: 'BLOCKED', attempts: sanitizedAttempts })}`)
  process.exit(1)
} finally {
  if (browser) await browser.close().catch(() => {})
}
