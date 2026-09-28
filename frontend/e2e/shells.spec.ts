import { expect, test } from '@playwright/test';

/** The M0 exit criterion, checked in a real browser: each shell loads, its
 * navigation is present, and both themes render. */
const APPS = [
  { name: 'customer', port: 5173, title: 'Kleim', nav: 'Main', first: 'Home' },
  { name: 'seller', port: 5174, title: 'Kleim for sellers', nav: 'Sections', first: 'Orders' },
  { name: 'rider', port: 5175, title: 'Kleim rider', nav: 'Main', first: 'Job' },
  { name: 'admin', port: 5176, title: 'Kleim admin', nav: 'Sections', first: 'Overview' },
];

for (const app of APPS) {
  test.describe(app.name, () => {
    const base = `http://localhost:${app.port}`;

    test('shell loads and shows its title', async ({ page }) => {
      await page.goto(base);
      await expect(page.getByRole('heading', { name: app.title })).toBeVisible();
    });

    test('navigation is present and labelled', async ({ page, isMobile }) => {
      await page.goto(base);
      // The sidebar apps only show navigation on a wide viewport, which is the
      // documented behaviour (Style Guide section 4.4), not a bug.
      const nav = page.getByRole('navigation', { name: app.nav });
      if (app.nav === 'Main' || !isMobile) {
        await expect(nav).toBeVisible();
        await expect(page.getByRole('link', { name: app.first })).toBeVisible();
      }
    });

    test('reports whether the API answered', async ({ page }) => {
      await page.goto(base);
      // Either outcome is a pass here: the point is that the shell says which,
      // rather than failing silently when the backend is not running.
      await expect(page.getByText(/API (reachable|unreachable)/)).toBeVisible();
    });

    test('renders in both themes', async ({ page }) => {
      await page.emulateMedia({ colorScheme: 'light' });
      await page.goto(base);
      const light = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);

      await page.emulateMedia({ colorScheme: 'dark' });
      const dark = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);

      expect(light).not.toBe(dark);
    });

    test('offers the component preview', async ({ page }) => {
      await page.goto(`${base}/preview`);
      await expect(page.getByRole('heading', { name: 'Components' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Place order' })).toHaveCount(0);
      await expect(page.getByRole('button', { name: 'primary' })).toBeVisible();
    });

    test('an unknown path explains itself', async ({ page }) => {
      await page.goto(`${base}/nope`);
      await expect(page.getByText('This page does not exist')).toBeVisible();
    });
  });
}
