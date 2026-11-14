import { defineConfig } from '@playwright/test';
import path from 'node:path';

const uiRoot = (process.env.GENESIS_BASE_URL ||
  'https://genesis-system3-web-doq2wplepa-el.a.run.app/ui').replace(/\/$/, '');
const localMode = process.env.GENESIS_UI_MODE === 'local';

export default defineConfig({
  testDir: '.',
  testMatch: 'genesis-ui-truth.spec.ts',
  timeout: 45_000,
  expect: { timeout: 5_000 },
  retries: 0,
  workers: 1,
  reporter: [['list']],
  outputDir: '../../reports/latest/playwright_ui_truth/test-results',
  webServer: localMode ? {
    command: 'npm run dev -- --host 127.0.0.1 --port 5173 --strictPort',
    cwd: path.resolve(process.cwd(), 'dashboard/frontend'),
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  } : undefined,
  use: {
    baseURL: uiRoot,
    browserName: 'chromium',
    timezoneId: 'Asia/Kolkata',
    launchOptions: process.env.PLAYWRIGHT_CHANNEL
      ? { channel: process.env.PLAYWRIGHT_CHANNEL }
      : {},
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
