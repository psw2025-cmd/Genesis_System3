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
  ['chain', 'Option Chain'],
  ['signals', 'Signals'],
  ['paper', 'Paper Trades'],
  ['positions', 'Positions'],
  ['broker', 'Broker'],
  ['performance', 'Performance'],
  ['ml', 'ML Model'],
  ['gates', 'Live Gate'],
]

const blockerWords = [
  'ERROR', 'FAIL', 'FAILED', 'BLOCKED', 'PEND', 'PENDING', 'NOT READY', 'NOT PROVEN',
  'NO TRADE', 'NO SIGNAL', '0/4', '0 / 4', 'MISSING', 'STALE', 'TIMEOUT',
  'INVALID', 'EXPIRED', 'UNAVAILABLE', 'UNHEALTHY', 'DEGRADED', 'AUTH REQUIRED',
]

function safeName(s) {
  return s.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '')
}

function uniq(items) {
  return Array.from(new Set(items.filter(Boolean)))
}

function isAllowedSafetyLine(text) {
  const t = String(text || '').toUpperCase()
  return (
    t.includes('LIVE') && (t.includes('OFF') || t.includes('BLOCKED') || t.includes('DISABLED'))
  ) || (
    t.includes('LIVE TRADING') && t.includes('BLOCKED BY BACKEND FLAG')
  )
}

async function authenticate(page) {
  if (!key) return { ok: false, status: 0, note: 'DASHBOARD_API_KEY missing' }
  try {
    const auth = await page.evaluate(async (apiKey) => {
      const r = await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
        credentials: 'include',
        body: JSON.stringify({ api_key: apiKey }),
      })
      return { ok: r.ok, status: r.status, text: await r.text() }
    }, key)
    return auth
  } catch (err) {
    return { ok: false, status: 0, error: String(err) }
  }
}

async function scanTab(page, id, title) {
  const result = {
    id,
    title,
    ok: false,
    screenshot: null,
    screenshot_ok: false,
    blocker_lines: [],
    red_elements: [],
    ui_exceptions: [],
  }

  try {
    const btn = page.locator(`button[title="${title}"]`).first()
    await btn.click({ timeout: 25000 })
    await page.waitForTimeout(4500)
    const screenshot = path.join(outDir, `${id}.png`)
    await page.screenshot({ path: screenshot, fullPage: true })
    result.screenshot = screenshot
    result.screenshot_ok = fs.existsSync(screenshot) && fs.statSync(screenshot).size > 10000

    const text = await page.locator('body').innerText({ timeout: 15000 }).catch(() => '')
    const lines = uniq(String(text).split('\n').map(x => x.trim()).filter(x => x.length > 1))
    result.blocker_lines = lines
      .filter(line => blockerWords.some(w => line.toUpperCase().includes(w)))
      .filter(line => !isAllowedSafetyLine(line))
      .slice(0, 120)

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

    result.blocker_lines = uniq([...result.blocker_lines, ...result.red_elements.map(x => x.text).filter(x => !isAllowedSafetyLine(x))]).slice(0, 150)
    result.ok = result.screenshot_ok && result.blocker_lines.length === 0
  } catch (err) {
    result.ui_exceptions.push(String(err).slice(0, 500))
  }
  return result
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1366, height: 768 }, extraHTTPHeaders: key ? { 'X-API-Key': key } : {} })
const page = await context.newPage()

const summary = {
  generated_at: new Date().toISOString(),
  base,
  status: 'UNKNOWN',
  auth: null,
  tabs: [],
  visible_issue_count: 0,
  screenshot_missing_count: 0,
  ui_exception_count: 0,
  visible_issues: [],
  todo: [],
  production_grade_claim_allowed: false,
}

try {
  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 90000 })
  await page.waitForTimeout(4000)
  summary.auth = await authenticate(page)
  await page.goto(`${base}/ui/`, { waitUntil: 'networkidle', timeout: 90000 })
  await page.waitForTimeout(5000)

  for (const [id, title] of tabs) {
    const r = await scanTab(page, id, title)
    summary.tabs.push(r)
    if (!r.screenshot_ok) summary.screenshot_missing_count += 1
    summary.ui_exception_count += r.ui_exceptions.length
    for (const line of r.blocker_lines) {
      summary.visible_issues.push({ tab: title, text: line })
      summary.todo.push(`Fix visible UI issue on ${title}: ${line}`)
    }
  }
} finally {
  await browser.close()
}

summary.visible_issues = summary.visible_issues.slice(0, 500)
summary.todo = uniq(summary.todo).slice(0, 500)
summary.visible_issue_count = summary.visible_issues.length
summary.status = summary.visible_issue_count || summary.screenshot_missing_count || summary.ui_exception_count ? 'BLOCKED' : 'PASS'

fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2))

const md = [
  '# Dashboard Visible Issue Tracker',
  '',
  `Generated: ${summary.generated_at}`,
  `Base: ${summary.base}`,
  `Status: **${summary.status}**`,
  `Visible issue count: \`${summary.visible_issue_count}\``,
  `Screenshot missing count: \`${summary.screenshot_missing_count}\``,
  `UI exception count: \`${summary.ui_exception_count}\``,
  '',
  '## Rule',
  '',
  'Any visible red/blocked/error/pending issue in the dashboard remains TODO until automated UI proof shows it is gone. Do not hide red states; fix the root cause or keep it marked BLOCKED.',
  '',
  '## TODO',
  '',
  ...(summary.todo.length ? summary.todo.map(x => `- [ ] ${x}`) : ['- [x] No visible UI blockers detected.']),
  '',
  '## Tab results',
  '',
  '| Tab | Status | Screenshot | Issues | Exceptions |',
  '|---|---|---:|---:|---:|',
  ...summary.tabs.map(t => `| ${t.title} | ${t.ok ? 'PASS' : 'BLOCKED'} | ${t.screenshot_ok ? 'OK' : 'MISSING'} | ${t.blocker_lines.length} | ${t.ui_exceptions.length} |`),
  '',
  '## Visible issues',
  '',
  ...(summary.visible_issues.length ? summary.visible_issues.map(x => `- **${x.tab}**: ${x.text}`) : ['- none']),
].join('\n')

fs.writeFileSync(path.join(outDir, 'summary.md'), md + '\n')

if (summary.status !== 'PASS') {
  console.error(`DASHBOARD_VISIBLE_ISSUES_BLOCKED issues=${summary.visible_issue_count} screenshots_missing=${summary.screenshot_missing_count} exceptions=${summary.ui_exception_count}`)
  process.exit(1)
}
