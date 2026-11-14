import { test, expect, Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const UI_ROOT = (process.env.GENESIS_BASE_URL ||
  'https://genesis-system3-web-doq2wplepa-el.a.run.app/ui').replace(/\/$/, '');
const ORIGIN = new URL(UI_ROOT).origin;
const LOCAL_UI_MODE = process.env.GENESIS_UI_MODE === 'local';
const ARTIFACT_DIR = path.resolve(process.env.PLAYWRIGHT_UI_ARTIFACTS || 'reports/latest/playwright_ui_truth');
const TABS = [
  { name: 'Board', id: 'decision-intel', query: '', content: '[data-testid="decision-intel-root"]', expected: 'Decision Intelligence' },
  { name: 'Live Gate', id: 'gates', query: '?tab=gates', content: '[data-testid="live-gate-flags"]', expected: 'Execution Truth & Live Gate' },
  { name: 'Prediction Audit', id: 'prediction-audit', query: '?tab=prediction-audit', content: '[data-testid="prediction-audit-root"]', expected: 'Prediction Audit Ledger' },
  { name: 'Multibagger', id: 'multibagger', query: '?tab=multibagger', content: '[data-testid="multibagger-root"]', expected: 'Multibagger Research Engine' },
  { name: 'Performance', id: 'performance', query: '?tab=performance', content: 'h2', expected: 'Performance' },
  { name: 'ML Model', id: 'ml', query: '?tab=ml', content: '[data-testid="ml-status"]', expected: 'ML Model Truth' },
  { name: 'System', id: 'system', query: '?tab=system', content: '[data-testid="system-token-truth-card"]', expected: 'Dhan Token & Connection Truth' },
];

function parseExchangeTimestamp(value: unknown): number {
  if (typeof value !== 'string' || !value.trim()) return Number.NaN;
  const raw = value.trim();
  const hasZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(raw);
  const parsed = Date.parse(hasZone ? raw : `${raw.replace(' ', 'T')}+05:30`);
  return Number.isFinite(parsed) ? parsed : Number.NaN;
}

function hasLiveMarketSource(candidate: Record<string, unknown>): boolean {
  const source = String(candidate.source ?? candidate.provider ?? '').trim().toUpperCase();
  const label = String(candidate.data_label ?? candidate.market_data_status ?? '').trim().toUpperCase();
  return ['DHAN', 'DHANHQ', 'NSE'].includes(source) &&
    (!label || ['LIVE', 'REALTIME', 'REAL_TIME'].includes(label));
}

function localApiPayload(pathname: string): Record<string, unknown> {
  if (pathname === '/api/ml/performance') {
    return { status: 'blocked', ready_for_live: false, live_trading_enabled: false, live_allowed: false, order_placement_allowed: false, real_broker_orders: false };
  }
  if (pathname === '/api/accuracy_trend') {
    return { status: 'no_data', trend: [], avg_rho: null, days_available: 0, retrain_needed: false };
  }
  if (pathname === '/api/auto_gates') return { status: 'ok', gates: {}, proof_gates: [], live_trading_enabled: false };
  if (pathname === '/api/state') {
    return { status: 'ok', mode: 'PAPER', live_trading_enabled: false, live_allowed: false, order_placement_allowed: false,
      market: { is_open: null, calendar_verified: false, calendar_status: 'UNKNOWN' }, broker: { connected: false }, signals: {} };
  }
  if (pathname === '/api/scanner/top_contract_gainers') return { status: 'unknown', market_open: null, market_top_table: [] };
  return { status: 'ok', ready_for_live: false, live_trading_enabled: false, live_allowed: false,
    order_placement_allowed: false, real_broker_orders: false, data: [], rows: [], contracts: [], candidates: [] };
}

async function openTab(page: Page, query: string, tabId?: string) {
  const failures: string[] = [];
  if (LOCAL_UI_MODE) {
    await page.route('**/api/**', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(localApiPayload(new URL(route.request().url()).pathname)),
    }));
  }
  page.on('pageerror', error => failures.push(`PAGE:${error.name}`));
  page.on('response', response => {
    if (response.url().includes('/api/') && response.status() >= 400) {
      failures.push(`API_HTTP_${response.status()}:${new URL(response.url()).pathname}`);
    }
  });
  page.on('requestfailed', request => {
    if (request.url().includes('/api/')) {
      const failure = request.failure()?.errorText || 'UNKNOWN';
      failures.push(`API_REQUEST_FAILED:${new URL(request.url()).pathname}:${failure}`);
    }
  });
  const pageBase = LOCAL_UI_MODE ? `${UI_ROOT}/` : UI_ROOT;
  await page.goto(`${pageBase}${query}`, { waitUntil: 'domcontentloaded', timeout: 30_000 });
  await expect(page.locator('#root')).toBeVisible();
  if (tabId) {
    await expect(page.locator(`[data-dashboard-tab="${tabId}"]`)).toHaveAttribute('aria-current', 'page', { timeout: 30_000 });
  }
  await page.waitForTimeout(750);
  await page.waitForFunction(() => {
    const text = document.body?.innerText || '';
    return !/LOADING VALIDATION|WAITING FOR \/API\/ACCURACY_TREND/i.test(text);
  }, null, { timeout: 30_000 });
  const visible = (await page.locator('#dashboard-main').innerText()).trim();
  expect(visible.length, 'selected tab must render meaningful main-panel content').toBeGreaterThan(20);
  return { failures, visible };
}

test.beforeAll(() => fs.mkdirSync(ARTIFACT_DIR, { recursive: true }));

test('seven production tabs render without long validation loading', async ({ page }) => {
  const { failures } = await openTab(page, TABS[0].query, TABS[0].id);
  const issues: string[] = [];
  for (const tab of TABS) {
    if (tab.id !== TABS[0].id) {
      await page.locator(`[data-dashboard-tab="${tab.id}"]`).click();
      await expect(page.locator(`[data-dashboard-tab="${tab.id}"]`)).toHaveAttribute('aria-current', 'page', { timeout: 30_000 });
      await page.waitForTimeout(750);
      await page.waitForFunction(() => {
        const text = document.body?.innerText || '';
        return !/LOADING VALIDATION|WAITING FOR \/API\/ACCURACY_TREND/i.test(text);
      }, null, { timeout: 30_000 });
    }
    const panel = page.locator('#dashboard-main');
    await expect(panel.locator(tab.content), `${tab.name} must mount its own content`).toBeVisible({ timeout: 30_000 });
    const visible = (await panel.innerText()).trim();
    if (!visible.toLowerCase().includes(tab.expected.toLowerCase())) issues.push(`${tab.name}:WRONG_PANEL_CONTENT`);
    const file = path.join(ARTIFACT_DIR, `${tab.name.toLowerCase().replace(/\W+/g, '-')}.png`);
    await page.screenshot({ path: file, fullPage: true });
    if (visible.length <= 20) issues.push(`${tab.name}:CONTENT_EMPTY`);
    if (/\bLIVE\s+ON\b/i.test(visible)) issues.push(`${tab.name}:LIVE_ON_LABEL`);
  }
  issues.push(...failures);
  expect(issues, 'tab content and browser/API errors').toEqual([]);
});

test('ML API readiness agrees with visible PAPER / LIVE OFF state', async ({ page }) => {
  let payload: Record<string, unknown>;
  if (LOCAL_UI_MODE) {
    payload = localApiPayload('/api/ml/performance');
  } else {
    const api = await page.request.get(`${ORIGIN}/api/ml/performance`, { timeout: 15_000 });
    expect(api.ok(), 'ML performance API must return successfully').toBeTruthy();
    payload = await api.json();
  }
  expect(typeof payload.ready_for_live, 'ready_for_live must be an explicit boolean').toBe('boolean');
  const { failures } = await openTab(page, '?tab=ml');
  const visible = (await page.locator('body').innerText()).trim();
  expect(visible).toMatch(/\bLIVE\s+OFF\b/i);
  expect(visible).not.toMatch(/\bLIVE\s+ON\b/i);
  for (const key of ['live_trading_enabled', 'live_allowed', 'order_placement_allowed', 'real_broker_orders']) {
    expect(payload[key], `${key} must not authorize real orders`).not.toBe(true);
  }
  expect(failures).toEqual([]);
});

test('Multibagger shows genuine candidates or calendar-proven closed state', async ({ page }) => {
  test.skip(LOCAL_UI_MODE, 'production candidate/calendar truth is verified only against the live service');
  const response = await page.request.get(`${ORIGIN}/api/scanner/top_contract_gainers?top_n=10`, { timeout: 15_000 });
  expect(response.ok(), 'scanner API must respond; timeout or HTTP error blocks UI acceptance').toBeTruthy();
  const payload = await response.json();
  const rows = [payload.candidates, payload.results, payload.data, payload.contracts, payload.market_top_table]
    .find(Array.isArray) as Array<Record<string, unknown>> | undefined;
  const candidates = rows || [];
  const stateResponse = await page.request.get(`${ORIGIN}/api/state`, { timeout: 15_000 });
  expect(stateResponse.ok(), 'state API must expose calendar evidence').toBeTruthy();
  const state = await stateResponse.json();
  const calendar = (state.market?.calendar_proof && typeof state.market.calendar_proof === 'object')
    ? state.market.calendar_proof as Record<string, unknown> : {};
  const evaluatedAt = Date.parse(String(calendar.evaluated_at_utc || ''));
  const proofAgeMs = Date.now() - evaluatedAt;
  const istToday = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date());
  const calendarEvidenceFresh = calendar.verified === true &&
    String(calendar.evidence_type || '') === 'OFFICIAL_NSE_FO_CIRCULAR_CACHE' &&
    String(calendar.session_date || '') === istToday &&
    Number.isFinite(evaluatedAt) && proofAgeMs >= -5_000 && proofAgeMs <= 5 * 60_000 &&
    /^https:\/\/nsearchives\.nseindia\.com\//i.test(String(calendar.source_url || '')) &&
    /^[a-f0-9]{64}$/i.test(String(calendar.calendar_sha256 || ''));
  const marketClosedWithProof = payload.market_open === false && calendarEvidenceFresh &&
    calendar.is_open === false && String(calendar.session_status) === 'CLOSED';
  const marketOpenWithProof = payload.market_open === true && calendarEvidenceFresh &&
    calendar.is_open === true && String(calendar.session_status) === 'OPEN';

  const { failures, visible } = await openTab(page, '?tab=multibagger');
  if (marketClosedWithProof) {
    expect(visible).toMatch(/MARKET CLOSED/i);
    expect(candidates.length, 'closed market must not invent live candidates').toBe(0);
  } else {
    expect(marketOpenWithProof, 'market-open requires current official calendar proof; missing/conflicting proof is UNKNOWN').toBe(true);
    const now = Date.now();
    const genuine = candidates.filter(candidate => {
      const symbol = String(candidate.symbol || candidate.trading_symbol || '').trim();
      const price = Number(candidate.ltp ?? candidate.price ?? candidate.last_price);
    const stamp = parseExchangeTimestamp(candidate.exchange_timestamp ?? candidate.timestamp);
      const age = now - stamp;
      return Boolean(symbol) && Number.isFinite(price) && price > 0 && ![999, 9999].includes(price) &&
        Number.isFinite(stamp) && age >= -5_000 && age <= 60_000 &&
        hasLiveMarketSource(candidate);
    });
    expect(genuine.length, 'minimum 3 fresh genuine candidates; no dummy or replay rows').toBeGreaterThanOrEqual(3);
  }
  expect(failures).toEqual([]);
});
