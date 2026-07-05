import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: 'verify_all_ui_tabs.spec.ts',
  timeout: 90000,
  retries: 0,
  reporter: [['list']],
  use: {
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
  ],
});
