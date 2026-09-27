import { AppShell, BottomNav, IconButton, type NavItem, useTheme } from '@kleim/ui';
import { Outlet, useLocation } from 'react-router';

import { bottomNavLink } from '../lib/nav';

const NAV: NavItem[] = [
  { to: '/', label: 'Home' },
  { to: '/explore', label: 'Explore' },
  { to: '/orders', label: 'Orders' },
  { to: '/profile', label: 'Profile' },
];

export function Layout() {
  const { pathname } = useLocation();
  const { resolved, setPreference } = useTheme();

  return (
    <AppShell
      title="Kleim"
      headerActions={
        <IconButton
          label={resolved === 'dark' ? 'Switch to the light theme' : 'Switch to the dark theme'}
          onClick={() => setPreference(resolved === 'dark' ? 'light' : 'dark')}
        >
          {resolved === 'dark' ? '☀' : '☾'}
        </IconButton>
      }
      bottomNav={<BottomNav items={NAV} currentPath={pathname} renderLink={bottomNavLink} />}
    >
      <Outlet />
    </AppShell>
  );
}
