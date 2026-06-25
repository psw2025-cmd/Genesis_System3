import { test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const BASE_URL = process.env.DASHBOARD_URL || 'https://genesis-system3-backend.onrender.com/ui';
const OUT_DIR = path.join('..', '..', 'reports', 'latest', 'ui_route_verification');
const SCREENSHOT_DIR = path.join(OUT_DIR, 'screenshots');

const TABS = [
  'control', 'health', 'scanner', 'options', 'paper',
  'portfolio', 'accuracy', 'signals', 'alerts', 'logs', 'proof',
];

test('all tabs load and screenshot', async ({ page }) => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const consoleErrors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push(`pageerror: ${err.message}`));

  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_initial_control.png'), fullPage: true });

  const results: any[] = [];

  for (const tabId of TABS) {
    const errorsBefore = consoleErrors.length;
    const navItem = page.locator('.nav-item').filter({ has: page.locator(`text=`) });
    // Click via JS to set activeTab directly is fragile across Vue internals;
    // instead click the nav-item whose nav-label text matches known labels.
    const clicked = await page.evaluate((id) => {
      const items = Array.from(document.querySelectorAll('.nav-item'));
      // tabs are rendered in the same order as the `tabs` array in app.js
      const idx = ['control','health','scanner','options','paper','portfolio','accuracy','signals','alerts','logs','proof'].indexOf(id);
      if (idx >= 0 && items[idx]) {
        (items[idx] as HTMLElement).click();
        return true;
      }
      return false;
    }, tabId);

    await page.waitForTimeout(2000);

    const bodyText = (await page.locator('body').innerText().catch(() => '')) || '';
    const screenshotPath = path.join(SCREENSHOT_DIR, `${tabId}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    results.push({
      tab: tabId,
      clicked,
      bodyTextLength: bodyText.length,
      bodyTextSample: bodyText.slice(0, 300).replace(/\s+/g, ' '),
      newConsoleErrors: consoleErrors.slice(errorsBefore),
    });
    console.log(`TAB ${tabId}: clicked=${clicked} textLen=${bodyText.length} newErrors=${consoleErrors.length - errorsBefore}`);
  }

  fs.writeFileSync(path.join(OUT_DIR, 'tab_results.json'), JSON.stringify(results, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, 'all_console_errors.json'), JSON.stringify(consoleErrors, null, 2));
});
