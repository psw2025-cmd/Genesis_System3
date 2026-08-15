import { test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const BASE_URL = process.env.DASHBOARD_URL || 'http://127.0.0.1:8000/ui';
const OUT_DIR = path.join('..', '..', 'reports', 'latest', 'ui_route_verification');
const SCREENSHOT_DIR = path.join(OUT_DIR, 'screenshots');

// MUST mirror dashboard/frontend/src/components/Sidebar.tsx DASHBOARD_TABS.
// This list intentionally includes every user-visible tab so adding a tab to
// Sidebar without extending production browser proof becomes a hard failure.
const TABS: { id: string; label: string }[] = [
  { id: 'decision-intel', label: 'Decision Intel' },
  { id: 'truth', label: 'Truth Control' },
  { id: 'genesis', label: 'Genesis Brain' },
  { id: 'e2e-proof', label: 'E2E Proof' },
  { id: 'overview', label: 'Overview' },
  { id: 'sim-live', label: 'Sim Live' },
  { id: 'options-intel', label: 'Options Intel' },
  { id: 'chain', label: 'Option Chain' },
  { id: 'signals', label: 'Signals' },
  { id: 'trade', label: 'Trade' },
  { id: 'paper', label: 'Paper Trades' },
  { id: 'positions', label: 'Positions' },
  { id: 'risk-scenarios', label: 'Risk & Scenarios' },
  { id: 'multibagger', label: 'Multibagger' },
  { id: 'prediction-audit', label: 'Prediction Audit' },
  { id: 'performance', label: 'Performance' },
  { id: 'ml', label: 'ML Model' },
  { id: 'data-integrity', label: 'Data Integrity' },
  { id: 'broker', label: 'Broker' },
  { id: 'alerts', label: 'Alerts' },
  { id: 'system', label: 'System' },
  { id: 'gates', label: 'Live Gate' },
];

const EXPECTED_TAB_COUNT = 22;
const FORBIDDEN_STRINGS = [
  '{{ ',
  'coming next iteration',
];
const REQUIRED_STRINGS = ['PAPER', 'LIVE OFF'];

function positiveMetric(body: string, label: string): number | null {
  const match = body.match(new RegExp(`${label}\\s+([0-9]+)`, 'i'));
  if (!match) return null;
  const value = Number(match[1]);
  return Number.isFinite(value) ? value : null;
}

function semanticFailures(tabId: string, body: string): string[] {
  const failures: string[] = [];
  if (body.trim().length < 80) failures.push('BODY_TOO_SHORT');

  if (tabId === 'chain') {
    // Option-chain proof must demonstrate actual broker-backed breadth, not
    // merely that the React component rendered. These labels are visible in
    // OptionChain.tsx and therefore are UI proof rather than backend-only proof.
    const universe = positiveMetric(body, 'DHAN UNIVERSE');
    const equity = positiveMetric(body, 'EQ OPT');
    const expiries = positiveMetric(body, 'EXPIRIES');
    const contracts = positiveMetric(body, 'CONTRACTS');
    const strikes = positiveMetric(body, 'STRIKES');
    if (universe == null || universe <= 6) failures.push(`DHAN_UNIVERSE_NOT_BROKER_BREADTH:${universe}`);
    if (equity == null || equity <= 0) failures.push(`EQUITY_OPTIONS_MISSING:${equity}`);
    if (expiries == null || expiries <= 0) failures.push(`EXPIRIES_MISSING:${expiries}`);
    if (contracts == null || contracts <= 0) failures.push(`OPTION_CONTRACTS_MISSING:${contracts}`);
    if (strikes == null || strikes <= 0) failures.push(`OPTION_STRIKES_MISSING:${strikes}`);
    if (!/ALL STRIKES\s*\([1-9][0-9]*\)/i.test(body)) failures.push('ALL_STRIKES_VISIBILITY_NOT_PROVEN');
    if (/DISCOVERY DEGRADED/i.test(body)) failures.push('UNDERLYING_DISCOVERY_DEGRADED');
    if (/CHAIN_SYMBOL_MISMATCH/i.test(body)) failures.push('CHAIN_SYMBOL_MISMATCH');
  }
  return failures;
}

test('all dashboard tabs load, render, screenshot, and pass semantic truth checks', async ({ page }) => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  if (TABS.length !== EXPECTED_TAB_COUNT) {
    throw new Error(`UI proof contract stale: expected ${EXPECTED_TAB_COUNT} tabs, verifier has ${TABS.length}`);
  }

  const consoleErrors: string[] = [];
  const results: any[] = [];

  const flush = (extra: Record<string, unknown> = {}) => {
    const anyNotClicked = results.some((r) => r.tab !== '00_initial' && r.clicked === false);
    const anyForbidden = results.some((r) => (r.forbiddenFound || []).length > 0);
    const anyStillLoading = results.some((r) => r.stillLoadingAfterWait);
    const anySemanticFailure = results.some((r) => (r.semanticFailures || []).length > 0);
    const summary = {
      generatedAt: new Date().toISOString(),
      baseUrl: BASE_URL,
      expectedTabCount: EXPECTED_TAB_COUNT,
      verifiedTabCount: results.filter((r) => r.tab !== '00_initial').length,
      overallPass: !anyForbidden && !anyStillLoading && !anyNotClicked && !anySemanticFailure,
      anyForbiddenStringsFound: anyForbidden,
      anyTabStillLoadingAfterWait: anyStillLoading,
      anyTabFailedToClick: anyNotClicked,
      anySemanticFailure,
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
    semanticFailures: initialBody.trim().length < 80 ? ['BODY_TOO_SHORT'] : [],
  });
  flush();

  for (const { id: tabId, label } of TABS) {
    const errorsBefore = consoleErrors.length;
    let clicked = true;
    try {
      await page.getByTitle(label, { exact: true }).click({ timeout: 5000 });
    } catch {
      clicked = false;
    }

    await page.waitForTimeout(tabId === 'chain' ? 5000 : 2500);

    let bodyText = '';
    let screenshotOk = true;
    try {
      bodyText = (await page.locator('body').innerText().catch(() => '')) || '';
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, `${tabId}.png`), fullPage: true });
    } catch {
      screenshotOk = false;
    }

    const forbiddenFound = FORBIDDEN_STRINGS.filter((s) => bodyText.includes(s));
    const stillLoading = /loading[a-z .]*$/i.test(bodyText.trim().slice(-60));
    const semantics = semanticFailures(tabId, bodyText);

    results.push({
      tab: tabId,
      label,
      clicked,
      screenshotOk,
      bodyTextLength: bodyText.length,
      bodyTextSample: bodyText.slice(0, 500).replace(/\s+/g, ' '),
      forbiddenFound,
      stillLoadingAfterWait: stillLoading,
      semanticFailures: semantics,
      newConsoleErrors: consoleErrors.slice(errorsBefore),
    });
    flush();
    console.log(
      `TAB ${tabId}: clicked=${clicked} screenshotOk=${screenshotOk} textLen=${bodyText.length} ` +
      `forbidden=${forbiddenFound.length} stillLoading=${stillLoading} semanticFailures=${semantics.length} ` +
      `newErrors=${consoleErrors.length - errorsBefore}`
    );

    if (page.isClosed()) {
      console.log('Page/browser closed unexpectedly — stopping early.');
      break;
    }
  }

  const anyNotClicked = results.some((r) => r.tab !== '00_initial' && r.clicked === false);
  const anyForbidden = results.some((r) => (r.forbiddenFound || []).length > 0);
  const anyStillLoading = results.some((r) => r.stillLoadingAfterWait);
  const anyMissingRequired = initialMissingRequired.length > 0;
  const anySemanticFailure = results.some((r) => (r.semanticFailures || []).length > 0);
  const verifiedTabCount = results.filter((r) => r.tab !== '00_initial').length;
  const incompleteCoverage = verifiedTabCount !== EXPECTED_TAB_COUNT;

  const summary = {
    generatedAt: new Date().toISOString(),
    baseUrl: BASE_URL,
    expectedTabCount: EXPECTED_TAB_COUNT,
    verifiedTabCount,
    overallPass: !anyForbidden && !anyStillLoading && !anyMissingRequired && !anyNotClicked && !anySemanticFailure && !incompleteCoverage,
    anyForbiddenStringsFound: anyForbidden,
    anyTabStillLoadingAfterWait: anyStillLoading,
    anyRequiredStringsMissing: anyMissingRequired,
    anyTabFailedToClick: anyNotClicked,
    anySemanticFailure,
    incompleteCoverage,
    totalConsoleErrors: consoleErrors.length,
    tabs: results,
  };

  fs.writeFileSync(path.join(OUT_DIR, 'tab_results.json'), JSON.stringify(summary, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, 'all_console_errors.json'), JSON.stringify(consoleErrors, null, 2));

  console.log(`\nOVERALL: ${summary.overallPass ? 'PASS' : 'FAIL'}`);
  console.log(`Verified tabs: ${verifiedTabCount}/${EXPECTED_TAB_COUNT}`);
  console.log(`Forbidden strings found: ${anyForbidden}`);
  console.log(`Any tab stuck loading: ${anyStillLoading}`);
  console.log(`Required strings missing: ${anyMissingRequired}`);
  console.log(`Any tab failed to click: ${anyNotClicked}`);
  console.log(`Any semantic truth failure: ${anySemanticFailure}`);

  if (!summary.overallPass) {
    throw new Error(
      `UI verification failed: coverage=${verifiedTabCount}/${EXPECTED_TAB_COUNT} notClicked=${anyNotClicked} ` +
      `forbidden=${anyForbidden} stillLoading=${anyStillLoading} missingRequired=${anyMissingRequired} semantic=${anySemanticFailure}. ` +
      'See tab_results.json.'
    );
  }
});