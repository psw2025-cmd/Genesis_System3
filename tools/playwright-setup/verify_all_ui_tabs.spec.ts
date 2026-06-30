import { test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Updated for the React rebuild (was Vue tab IDs: control/health/scanner/...).
// Current Sidebar.tsx nav-item order: overview, trade, positions, broker,
// performance, alerts, system, gates.
const BASE_URL = process.env.DASHBOARD_URL || 'https://genesis-system3-backend.onrender.com/ui';
const OUT_DIR = path.join('..', '..', 'reports', 'latest', 'ui_route_verification');
const SCREENSHOT_DIR = path.join(OUT_DIR, 'screenshots');

const TABS = [
  'overview', 'trade', 'positions', 'broker',
  'performance', 'alerts', 'system', 'gates',
];

// Strings that must never appear on a production React build of this
// dashboard — leftover Vue templating, the old hardcoded Performance
// placeholder, or a sign that data never resolved.
const FORBIDDEN_STRINGS = [
  '{{ ',
  'coming next iteration',
];

const REQUIRED_STRINGS = ['PAPER', 'LIVE OFF'];

test('all tabs load, screenshot, and pass content checks', async ({ page }) => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const consoleErrors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push(`pageerror: ${err.message}`));

  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_initial_overview.png'), fullPage: true });

  const initialBody = (await page.locator('body').innerText().catch(() => '')) || '';
  const initialForbidden = FORBIDDEN_STRINGS.filter((s) => initialBody.includes(s));
  const initialMissingRequired = REQUIRED_STRINGS.filter((s) => !initialBody.includes(s));

  const results: any[] = [{
    tab: '00_initial',
    forbiddenFound: initialForbidden,
    missingRequired: initialMissingRequired,
    bodyTextLength: initialBody.length,
  }];

  for (const tabId of TABS) {
    const errorsBefore = consoleErrors.length;

    const clicked = await page.evaluate((id) => {
      const items = Array.from(document.querySelectorAll('.nav-item'));
      const tabOrder = ['overview', 'trade', 'positions', 'broker', 'performance', 'alerts', 'system', 'gates'];
      const idx = tabOrder.indexOf(id);
      if (idx >= 0 && items[idx]) {
        (items[idx] as HTMLElement).click();
        return true;
      }
      return false;
    }, tabId);

    await page.waitForTimeout(2500);

    const bodyText = (await page.locator('body').innerText().catch(() => '')) || '';
    const forbiddenFound = FORBIDDEN_STRINGS.filter((s) => bodyText.includes(s));
    // "Loading..." text alone is fine right after click; only flag if a
    // loading-shaped string is STILL there after the wait above settles —
    // a crude but effective endless-loading detector.
    const stillLoading = /loading[a-z .]*$/i.test(bodyText.trim().slice(-60));

    const screenshotPath = path.join(SCREENSHOT_DIR, `${tabId}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    results.push({
      tab: tabId,
      clicked,
      bodyTextLength: bodyText.length,
      bodyTextSample: bodyText.slice(0, 300).replace(/\s+/g, ' '),
      forbiddenFound,
      stillLoadingAfterWait: stillLoading,
      newConsoleErrors: consoleErrors.slice(errorsBefore),
    });
    console.log(
      `TAB ${tabId}: clicked=${clicked} textLen=${bodyText.length} ` +
      `forbidden=${forbiddenFound.length} stillLoading=${stillLoading} ` +
      `newErrors=${consoleErrors.length - errorsBefore}`
    );
  }

  const anyForbidden = results.some((r) => (r.forbiddenFound || []).length > 0);
  const anyStillLoading = results.some((r) => r.stillLoadingAfterWait);
  const anyMissingRequired = (initialMissingRequired || []).length > 0;

  const summary = {
    generatedAt: new Date().toISOString(),
    baseUrl: BASE_URL,
    overallPass: !anyForbidden && !anyStillLoading && !anyMissingRequired,
    anyForbiddenStringsFound: anyForbidden,
    anyTabStillLoadingAfterWait: anyStillLoading,
    anyRequiredStringsMissing: anyMissingRequired,
    totalConsoleErrors: consoleErrors.length,
    tabs: results,
  };

  fs.writeFileSync(path.join(OUT_DIR, 'tab_results.json'), JSON.stringify(summary, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, 'all_console_errors.json'), JSON.stringify(consoleErrors, null, 2));

  console.log(`\nOVERALL: ${summary.overallPass ? 'PASS' : 'FAIL'}`);
  console.log(`Forbidden strings found: ${anyForbidden}`);
  console.log(`Any tab stuck loading: ${anyStillLoading}`);
  console.log(`Required strings missing: ${anyMissingRequired}`);
});
