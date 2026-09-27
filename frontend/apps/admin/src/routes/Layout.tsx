import { AppShell, IconButton, Sidebar, type NavItem, useTheme } from '@kleim/ui';
import { Outlet, useLocation } from 'react-router';

import { sidebarLink } from '../lib/nav';

const NAV: NavItem[] = [
  { to: '/', label: 'Overview' },
  { to: '/approvals', label: 'Approvals' },
  { to: '/exceptions', label: 'Exceptions' },
  { to: '/audit', label: 'Audit' },
];

export function Layout() {
  const { pathname } = useLocation();
  const { resolved, setPreference } = useTheme();

  return (
    <AppShell
      title="Kleim admin"
      headerActions={
        <IconButton
          label={resolved === 'dark' ? 'Switch to the light theme' : 'Switch to the dark theme'}
          onClick={() => setPreference(resolved === 'dark' ? 'light' : 'dark')}
        >
          {resolved === 'dark' ? '☀' : '☾'}
        </IconButton>
      }
      sidebar={
        <Sidebar
          items={NAV}
          currentPath={pathname}
          renderLink={sidebarLink}
          brand={<span className="text-section">Kleim</span>}
        />
      }
    >
      <Outlet />
    </AppShell>
  );
}
