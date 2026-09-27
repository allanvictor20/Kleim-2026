import { clsx } from 'clsx';
import type { NavItem } from '@kleim/ui';
import { NavLink } from 'react-router';

/** Bottom-nav and sidebar items render through the app's router, so
 * `@kleim/ui` stays router-agnostic. `aria-current` marks the current page. */
export function bottomNavLink(item: NavItem, isCurrent: boolean) {
  return (
    <NavLink
      key={item.to}
      to={item.to}
      end
      aria-current={isCurrent ? 'page' : undefined}
      className={clsx(
        'flex min-h-[var(--tap)] flex-1 flex-col items-center justify-center gap-1 py-2',
        'text-caption font-bold',
        isCurrent ? 'text-link' : 'text-muted',
      )}
    >
      {item.label}
    </NavLink>
  );
}

export function sidebarLink(item: NavItem, isCurrent: boolean) {
  return (
    <NavLink
      key={item.to}
      to={item.to}
      end
      aria-current={isCurrent ? 'page' : undefined}
      className={clsx(
        'text-small flex min-h-[var(--tap)] items-center rounded-md px-3 font-bold',
        isCurrent ? 'bg-side-3 text-on-dark' : 'text-on-dark/70 hover:bg-side-2',
      )}
    >
      {item.label}
    </NavLink>
  );
}
