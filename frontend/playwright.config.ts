import { defineConfig, devices } from '@playwright/test';

/** End-to-end smoke tests for the four app shells.
 *
 * Runs against the production build rather than the dev server: that is what a
 * customer in Kampala actually loads, and it catches a token or asset that only
 * breaks once bundled. The core order-flow spec CONTRIBUTING.md section 6 asks
 * for belongs to M5, when there is a flow to walk.
 */
const APPS = [
  { name: 'customer', port: 5173 },
  { name: 'seller', port: 5174 },
  { name: 'rider', port: 5175 },
  { name: 'admin', port: 5176 },
];

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : [['list']],
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    // Escape hatch for images that ship their own Chromium (some CI runners and
    // dev containers do) instead of letting Playwright download one. Leave it
    // unset locally and `pnpm exec playwright install chromium` provides the
    // matching build.
    ...(process.env.PLAYWRIGHT_CHROMIUM_PATH
      ? { launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH } }
      : {}),
  },
  projects: [
    {
      // A mid-range Android phone on a slow connection is the real target
      // (NFR-05 to NFR-07), so the default project is a phone, not a desktop.
      name: 'phone',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: APPS.map((app) => ({
    command: `pnpm --filter @kleim/${app.name}-app preview`,
    url: `http://localhost:${app.port}`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  })),
});
