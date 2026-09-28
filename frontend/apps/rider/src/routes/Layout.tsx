import { AppShell, BottomNav, IconButton, type NavItem, useTheme } from '@kleim/ui';
import { Outlet, useLocation } from 'react-router';

import { bottomNavLink } from '../lib/nav';

const NAV: NavItem[] = [
  { to: '/', label: 'Job' },
  { to: '/offers', label: 'Offers' },
  { to: '/earnings', label: 'Earnings' },
  { to: '/profile', label: 'Profile' },
];

export function Layout() {
  const { pathname } = useLocation();
  const { resolved, setPreference } = useTheme();

  return (
    <AppShell
      title="Kleim rider"
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
