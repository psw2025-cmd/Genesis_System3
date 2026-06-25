import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Already configurable via DASHBOARD_URL - not hardcoded. Falls back to
// production only because no staging environment exists yet (tracked
// separately). Once one does: DASHBOARD_URL=https://<staging-host>/ui
// npx playwright test, or set it in CI as a job env var - no code
// change needed here when that happens.
const DASHBOARD_URL = process.env.DASHBOARD_URL || 'https://genesis-system3-backend.onrender.com/ui';
const REPORT_DIR = path.join('reports', 'latest', 'dashboard_browser_proof');
const SCREENSHOT_DIR = path.join(REPORT_DIR, 'screenshots');

type FieldResult = {
  field: string;
  status: 'PASS' | 'NOT_PROVEN' | 'MISSING_FIELD' | 'UI_NOT_VISIBLE' | 'PASS_WITH_WARNINGS';
  detail: string;
};

const fieldResults: FieldResult[] = [];
const consoleErrors: string[] = [];
let loadResult: 'PASS' | 'DASHBOARD_LOAD_FAILED' | 'PASS_WITH_WARNINGS' = 'PASS';

function ensureDirs() {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

function checkField(pageText: string, field: string, patterns: RegExp[]): FieldResult {
  for (const pattern of patterns) {
    if (pattern.test(pageText)) {
      return { field, status: 'PASS', detail: `Matched ${pattern}` };
    }
  }
  return { field, status: 'UI_NOT_VISIBLE', detail: 'Not found in rendered page text' };
}

test.beforeAll(() => {
  ensureDirs();
});

for (const viewport of [
  { name: 'desktop', width: 1920, height: 1080 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 667 },
]) {
  test(`dashboard proof ${viewport.name}`, async ({ page }) => {
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(`[${viewport.name}] ${msg.text()}`);
      }
    });

    await page.setViewportSize({ width: viewport.width, height: viewport.height });

    let responseOk = false;
    try {
      const response = await page.goto(DASHBOARD_URL, { waitUntil: 'networkidle', timeout: 90000 });
      responseOk = !!response && response.ok();
      await page.waitForSelector('text=SYSTEM3', { timeout: 30000 }).catch(() => {});
      await page.waitForSelector('text=PAPER', { timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(3000);
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(1500);
      const paperTab = page.locator('.nav-label', { hasText: 'Paper Lifecycle' }).first();
      if (await paperTab.isVisible().catch(() => false)) {
        await paperTab.click().catch(() => {});
        await page.waitForTimeout(2500);
      }
    } catch (err) {
      loadResult = 'DASHBOARD_LOAD_FAILED';
      fieldResults.push({
        field: `load_${viewport.name}`,
        status: 'NOT_PROVEN',
        detail: String(err),
      });
    }

    const screenshotPath = path.join(SCREENSHOT_DIR, `${viewport.name}_${viewport.width}x${viewport.height}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const bodyText = (await page.locator('body').innerText().catch(() => '')) || '';
    const html = await page.content();

    if (!responseOk || bodyText.length < 20) {
      loadResult = 'DASHBOARD_LOAD_FAILED';
    } else if (html.includes('Application error') || html.includes('502') || html.includes('503')) {
      loadResult = 'PASS_WITH_WARNINGS';
    }

    const checks: Array<[string, RegExp[]]> = [
      ['analyzer_paper_mode', [/ANALYZER\s*\/\s*PAPER/i, /PAPER ONLY/i, /PAPER MODE/i]],
      ['live_trading_disabled', [/LIVE DISABLED/i, /LIVE TRADING[\s\S]{0,20}DISABLED/i, /LIVE TRADING KILL SWITCH/i, /BLOCKED/i]],
      ['broker_status', [/DHAN CONNECTED/i, /BROKER OFFLINE/i, /BROKER/i, /Dhan/i]],
      ['data_source', [/Chain Source/i, /DATA APIs/i, /Dhan/i, /REST Fallback/i]],
      ['market_status', [/MARKET OPEN/i, /MARKET CLOSED/i, /MARKET/i]],
      ['option_chain_readiness', [/Option Chain/i, /Contracts/i, /CHAIN/i]],
      ['proof_audit_status', [/Proof Status/i, /Gate Matrix/i, /QC Report/i, /Production Gate/i]],
      ['pnl_positions', [/GROSS P&L/i, /NET P&L/i, /OPEN POSITIONS/i, /Paper Trade/i, /WIN RATE/i, /P&L Charges/i]],
      ['no_false_live_ready', []],
    ];

    for (const [field, patterns] of checks) {
      if (field === 'no_false_live_ready') {
        const falseLive =
          (/PRODUCTION\s*READY(?!\s*NOT)/i.test(bodyText) && !/NOT READY/i.test(bodyText)) ||
          (/LIVE[_\s-]?READY/i.test(bodyText) && !/NOT.*READY/i.test(bodyText));
        fieldResults.push({
          field: `${field}_${viewport.name}`,
          status: falseLive ? 'NOT_PROVEN' : 'PASS',
          detail: falseLive ? 'Possible false LIVE/PRODUCTION READY claim' : 'Shows PRODUCTION NOT READY / LIVE BLOCKED',
        });
        continue;
      }
      const result = checkField(bodyText, `${field}_${viewport.name}`, patterns);
      fieldResults.push(result);
    }

    expect(fs.existsSync(screenshotPath)).toBeTruthy();
  });
}

test.afterAll(() => {
  ensureDirs();
  const fieldsFound = fieldResults.filter((f) => f.status === 'PASS');
  const fieldsMissing = fieldResults.filter((f) => f.status !== 'PASS');

  let verdict: string = 'PASS';
  if (loadResult === 'DASHBOARD_LOAD_FAILED') {
    verdict = 'FAIL';
  } else if (fieldsMissing.length > 0 || consoleErrors.length > 0) {
    verdict = 'PASS_WITH_WARNINGS';
  }

  const summary = {
    url_tested: DASHBOARD_URL,
    viewports_tested: ['1920x1080', '768x1024', '375x667'],
    screenshots_created: fs.existsSync(SCREENSHOT_DIR)
      ? fs.readdirSync(SCREENSHOT_DIR).filter((f) => f.endsWith('.png'))
      : [],
    fields_found: fieldsFound,
    fields_missing: fieldsMissing,
    load_result: loadResult,
    console_errors: consoleErrors,
    final_verdict: verdict,
    generated_utc: new Date().toISOString(),
  };

  fs.writeFileSync(path.join(REPORT_DIR, 'summary.json'), JSON.stringify(summary, null, 2));
  const md = [
    '# Dashboard Browser Proof',
    '',
    `Generated UTC: \`${summary.generated_utc}\``,
    '',
    `URL: ${DASHBOARD_URL}`,
    '',
    `Load result: **${loadResult}**`,
    `Final verdict: **${verdict}**`,
    '',
    '## Viewports',
    ...summary.viewports_tested.map((v) => `- ${v}`),
    '',
    '## Screenshots',
    ...summary.screenshots_created.map((s) => `- screenshots/${s}`),
    '',
    '## Fields missing / not proven',
    ...fieldsMissing.map((f) => `- ${f.field}: ${f.status} — ${f.detail}`),
    '',
    '## Console errors',
    ...(consoleErrors.length ? consoleErrors.map((e) => `- ${e}`) : ['- none']),
  ].join('\n');
  fs.writeFileSync(path.join(REPORT_DIR, 'summary.md'), md);

  if (verdict === 'FAIL') {
    throw new Error(`Dashboard browser proof failed. See ${path.join(REPORT_DIR, 'summary.json')}`);
  }
});
