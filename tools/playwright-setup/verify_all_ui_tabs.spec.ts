import { test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Sidebar.tsx (as of 2026-07-03) renders each tab as a plain <button
// title={label}> with NO className — there is no ".nav-item" class in the
// current build. The previous version of this spec selected `.nav-item`,
// which matches zero elements against the live site, so every tab "click"
// silently returned false and every screenshot after 00_initial was just
// the overview page again — a false PASS that never actually exercised any
// tab. Selecting by the button's `title` attribute (which IS present and
// unique per tab) actually drives real navigation.
const BASE_URL = process.env.DASHBOARD_URL || 'https://genesis-system3-backend.onrender.com/ui';
const OUT_DIR = path.join('..', '..', 'reports', 'latest', 'ui_route_verification');
const SCREENSHOT_DIR = path.join(OUT_DIR, 'screenshots');

// Full current tab list from dashboard/frontend/src/components/Sidebar.tsx
// TABS array: { id, label }. Must be kept in sync with that file.
const TABS: { id: string; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'chain', label: 'Option Chain' },
  { id: 'signals', label: 'Signals' },
  { id: 'trade', label: 'Trade' },
  { id: 'paper', label: 'Paper Trades' },
  { id: 'positions', label: 'Positions' },
  { id: 'performance', label: 'Performance' },
  { id: 'ml', label: 'ML Model' },
  { id: 'broker', label: 'Broker' },
  { id: 'alerts', label: 'Alerts' },
  { id: 'system', label: 'System' },
  { id: 'gates', label: 'Live Gate' },
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
  const results: any[] = [];

  // Write whatever we have so far to disk after every step, and print each
  // console/page error the instant it happens. If the page (or the whole
  // browser) crashes mid-run, a crash-terminated test used to lose all of
  // this in memory — the results file never got written and the run looked
  // like it silently vanished. Now every tab's outcome is on disk and in
  // stdout before we ever move to the next tab.
  const flush = (extra: Record<string, unknown> = {}) => {
    const anyNotClicked = results.some((r) => r.tab !== '00_initial' && r.clicked === false);
    const anyForbidden = results.some((r) => (r.forbiddenFound || []).length > 0);
    const anyStillLoading = results.some((r) => r.stillLoadingAfterWait);
    const summary = {
      generatedAt: new Date().toISOString(),
      baseUrl: BASE_URL,
      overallPass: !anyForbidden && !anyStillLoading && !anyNotClicked,
      anyForbiddenStringsFound: anyForbidden,
      anyTabStillLoadingAfterWait: anyStillLoading,
      anyTabFailedToClick: anyNotClicked,
      totalConsoleErrors: consoleErrors.length,
      tabs: results,
      ...extra,
    };
    fs.writeFileSync(path.join(OUT_DIR, 'tab_results.json'), JSON.stringify(summary, null, 2));
    fs.writeFileSync(path.join(OUT_DIR, 'all_console_errors.json'), JSON.stringify(consoleErrors, null, 2));
    return summary;
  };

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text();
      consoleErrors.push(text);
      console.log(`[console.error] ${text}`);
    }
  });
  page.on('pageerror', (err) => {
    const text = `pageerror: ${err.message}`;
    consoleErrors.push(text);
    console.log(`[PAGE CRASH] ${text}`);
  });

  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_initial_overview.png'), fullPage: true });

  const initialBody = (await page.locator('body').innerText().catch(() => '')) || '';
  const initialForbidden = FORBIDDEN_STRINGS.filter((s) => initialBody.includes(s));
  const initialMissingRequired = REQUIRED_STRINGS.filter((s) => !initialBody.includes(s));

  results.push({
    tab: '00_initial',
    forbiddenFound: initialForbidden,
    missingRequired: initialMissingRequired,
    bodyTextLength: initialBody.length,
  });
  flush();

  for (const { id: tabId, label } of TABS) {
    const errorsBefore = consoleErrors.length;

    let clicked = true;
    try {
      await page.getByTitle(label, { exact: true }).click({ timeout: 5000 });
    } catch (e) {
      clicked = false;
    }

    await page.waitForTimeout(2500);

    let bodyText = '';
    let screenshotOk = true;
    try {
      bodyText = (await page.locator('body').innerText().catch(() => '')) || '';
      const screenshotPath = path.join(SCREENSHOT_DIR, `${tabId}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
    } catch (e) {
      screenshotOk = false;
    }

    const forbiddenFound = FORBIDDEN_STRINGS.filter((s) => bodyText.includes(s));
    // "Loading..." text alone is fine right after click; only flag if a
    // loading-shaped string is STILL there after the wait above settles —
    // a crude but effective endless-loading detector.
    const stillLoading = /loading[a-z .]*$/i.test(bodyText.trim().slice(-60));

    results.push({
      tab: tabId,
      label,
      clicked,
      screenshotOk,
      bodyTextLength: bodyText.length,
      bodyTextSample: bodyText.slice(0, 300).replace(/\s+/g, ' '),
      forbiddenFound,
      stillLoadingAfterWait: stillLoading,
      newConsoleErrors: consoleErrors.slice(errorsBefore),
    });
    flush();
    console.log(
      `TAB ${tabId}: clicked=${clicked} screenshotOk=${screenshotOk} textLen=${bodyText.length} ` +
      `forbidden=${forbiddenFound.length} stillLoading=${stillLoading} ` +
      `newErrors=${consoleErrors.length - errorsBefore}`
    );

    // If the page (or browser) has died, stop iterating rather than let
    // every remaining tab time out one by one burning the whole test budget.
    if (page.isClosed()) {
      console.log('Page/browser closed unexpectedly — stopping early.');
      break;
    }
  }

  const anyNotClicked = results.some((r) => r.tab !== '00_initial' && r.clicked === false);

  const anyForbidden = results.some((r) => (r.forbiddenFound || []).length > 0);
  const anyStillLoading = results.some((r) => r.stillLoadingAfterWait);
  const anyMissingRequired = (initialMissingRequired || []).length > 0;

  const summary = {
    generatedAt: new Date().toISOString(),
    baseUrl: BASE_URL,
    overallPass: !anyForbidden && !anyStillLoading && !anyMissingRequired && !anyNotClicked,
    anyForbiddenStringsFound: anyForbidden,
    anyTabStillLoadingAfterWait: anyStillLoading,
    anyRequiredStringsMissing: anyMissingRequired,
    anyTabFailedToClick: anyNotClicked,
    totalConsoleErrors: consoleErrors.length,
    tabs: results,
  };

  fs.writeFileSync(path.join(OUT_DIR, 'tab_results.json'), JSON.stringify(summary, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, 'all_console_errors.json'), JSON.stringify(consoleErrors, null, 2));

  console.log(`\nOVERALL: ${summary.overallPass ? 'PASS' : 'FAIL'}`);
  console.log(`Forbidden strings found: ${anyForbidden}`);
  console.log(`Any tab stuck loading: ${anyStillLoading}`);
  console.log(`Required strings missing: ${anyMissingRequired}`);
  console.log(`Any tab failed to click: ${anyNotClicked}`);

  if (anyNotClicked || anyForbidden || anyStillLoading || anyMissingRequired) {
    throw new Error(
      `UI verification failed: notClicked=${anyNotClicked} forbidden=${anyForbidden} ` +
      `stillLoading=${anyStillLoading} missingRequired=${anyMissingRequired}. See tab_results.json.`
    );
  }
});
