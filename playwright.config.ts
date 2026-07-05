import { defineConfig, devices } from '@playwright/test';

const DASHBOARD_URL = process.env.DASHBOARD_URL || 'https://genesis-system3-backend.onrender.com/ui';
const SCREENSHOT_DIR = 'reports/latest/dashboard_browser_proof/screenshots';

export default defineConfig({
  testDir: './tests',
  testMatch: 'dashboard_browser_proof.spec.ts',
  timeout: 90000,
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: DASHBOARD_URL,
    trace: 'off',
    screenshot: 'off',
  },
  projects: [
    {
      name: 'desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'tablet',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 768, height: 1024 },
      },
    },
    {
      name: 'mobile',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 375, height: 667 },
      },
    },
  ],
  outputDir: SCREENSHOT_DIR,
});
