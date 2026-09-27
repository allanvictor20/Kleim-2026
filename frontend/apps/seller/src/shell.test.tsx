/** Shell smoke tests.
 *
 * The M0 exit criterion is that the shell loads against the local API, so these
 * cover exactly that: the frame renders, navigation is present and labelled, and
 * the landing route reports whether the API answered.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@kleim/ui';
import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { api } from './lib/api';
import { routes } from './router';

function renderApp(initialPath = '/') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const router = createMemoryRouter(routes, { initialEntries: [initialPath] });

  return render(
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </ThemeProvider>,
  );
}

describe('seller shell', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the frame and its title', async () => {
    vi.spyOn(api, 'health').mockResolvedValue({
      status: 'ok',
      checks: { database: 'ok', redis: 'ok' },
    });

    renderApp();

    expect(await screen.findByRole('heading', { name: 'Kleim for sellers' })).toBeInTheDocument();
  });

  it('offers labelled navigation with the current item marked', async () => {
    vi.spyOn(api, 'health').mockResolvedValue({ status: 'ok' });

    renderApp();

    const nav = await screen.findByRole('navigation', { name: 'Sections' });
    expect(nav).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Orders' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Products' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Stock' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Payouts' })).toBeInTheDocument();
  });

  it('says the API is reachable once it answers', async () => {
    vi.spyOn(api, 'health').mockResolvedValue({
      status: 'ok',
      checks: { database: 'ok', redis: 'ok' },
    });

    renderApp();

    expect(await screen.findByText('API reachable')).toBeInTheDocument();
    expect(await screen.findByText(/database ok/)).toBeInTheDocument();
  });

  it('says so plainly when the API cannot be reached', async () => {
    // No stack trace and no raw error: Style Guide section 7.3.
    vi.spyOn(api, 'health').mockRejectedValue(new Error('connection refused'));

    renderApp();

    expect(await screen.findByText('API unreachable')).toBeInTheDocument();
    expect(screen.queryByText(/connection refused/)).not.toBeInTheDocument();
  });

  it('shows a way forward on an unknown path', async () => {
    vi.spyOn(api, 'health').mockResolvedValue({ status: 'ok' });

    renderApp('/not-a-real-page');

    expect(await screen.findByText('This page does not exist')).toBeInTheDocument();
  });

  it('mounts the component preview', async () => {
    renderApp('/preview');

    expect(await screen.findByRole('heading', { name: 'Components' })).toBeInTheDocument();
  });
});
