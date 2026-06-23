import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

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
      const response = await page.goto(DASHBOARD_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
      responseOk = !!response && response.ok();
      await page.waitForTimeout(5000);
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
      ['analyzer_paper_mode', [/PAPER/i, /ANALYZER/i, /Paper/i]],
      ['live_trading_disabled', [/live trading disabled/i, /Live Trading.*Disabled/i, /order_placement_allowed.*false/i]],
      ['broker_status', [/broker/i, /dhan/i, /connected/i]],
      ['data_source', [/data source/i, /BROKER/i, /source/i]],
      ['market_status', [/market/i, /closed/i, /open/i]],
      ['option_chain_readiness', [/option.?chain/i, /chain/i, /contracts/i]],
      ['proof_audit_status', [/proof/i, /audit/i, /QC/i, /status/i]],
      ['pnl_positions', [/P&L/i, /PnL/i, /positions/i, /unrealized/i]],
      ['no_false_live_ready', []],
    ];

    for (const [field, patterns] of checks) {
      if (field === 'no_false_live_ready') {
        const falseLive = /LIVE[_\s-]?READY/i.test(bodyText) && !/NOT.*READY/i.test(bodyText);
        fieldResults.push({
          field: `${field}_${viewport.name}`,
          status: falseLive ? 'NOT_PROVEN' : 'PASS',
          detail: falseLive ? 'Possible false LIVE_READY claim' : 'No false LIVE_READY claim detected',
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
});
