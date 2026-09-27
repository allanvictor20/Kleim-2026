/** Layout shells — UI/UX Style Guide section 4.4.
 *
 * Under 520px: one column, full-bleed, fixed bottom navigation. 520-1180px: a
 * centred 400px column for customer and rider, two columns for seller and admin.
 * Over 1180px: sidebar plus content for seller and admin.
 *
 * Headers and bottom bars add `env(safe-area-inset-*)` padding so nothing hides
 * under a notch or a home indicator.
 */
import { clsx } from 'clsx';
import type { ReactNode } from 'react';

export interface NavItem {
  to: string;
  label: string;
  icon?: ReactNode;
}

export interface AppShellProps {
  title: string;
  children: ReactNode;
  /** Phone shell with bottom navigation: customer and rider. */
  bottomNav?: ReactNode;
  /** Desktop shell with a sidebar: seller and admin. */
  sidebar?: ReactNode;
  headerActions?: ReactNode;
}

export function AppShell({ title, children, bottomNav, sidebar, headerActions }: AppShellProps) {
  if (sidebar) {
    return (
      <div className="bg-page phone:flex min-h-dvh">
        {sidebar}
        {/* --page sits behind the frame; the content area is the app background. */}
        <div className="bg-screen flex min-w-0 flex-1 flex-col">
          <AppHeader title={title} actions={headerActions} />
          <main className="flex-1 px-[var(--screen-padding)] py-5">{children}</main>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-page flex min-h-dvh justify-center">
      <div className="bg-screen phone:shadow-[var(--shadow-raised)] flex w-full max-w-[400px] flex-col">
        <AppHeader title={title} actions={headerActions} />
        <main
          className={clsx(
            'flex-1 px-[var(--screen-padding)] py-4',
            // Leave room for the fixed bottom bar plus the home indicator.
            bottomNav && 'pb-[calc(76px+env(safe-area-inset-bottom,0px))]',
          )}
        >
          {children}
        </main>
        {bottomNav}
      </div>
    </div>
  );
}

export function AppHeader({ title, actions }: { title: string; actions?: ReactNode }) {
  return (
    <header
      className={clsx(
        'bg-card border-line sticky top-0 z-10 flex items-center justify-between gap-3',
        'border-b px-[var(--screen-padding)] pb-3',
        'pt-[calc(14px+env(safe-area-inset-top,0px))]',
      )}
    >
      <h1 className="text-display text-ink truncate">{title}</h1>
      {actions ? <div className="flex shrink-0 items-center gap-1">{actions}</div> : null}
    </header>
  );
}

/** Bottom navigation: four items, the current one marked with aria-current. */
export function BottomNav({
  items,
  currentPath,
  renderLink,
}: {
  items: NavItem[];
  currentPath: string;
  /** The app supplies its router's link, so this package stays router-agnostic. */
  renderLink: (item: NavItem, isCurrent: boolean) => ReactNode;
}) {
  return (
    <nav
      aria-label="Main"
      className={clsx(
        'bg-card border-line fixed bottom-0 z-10 w-full max-w-[400px] border-t',
        'flex items-stretch justify-around',
        'pb-[env(safe-area-inset-bottom,0px)]',
      )}
    >
      {items.map((item) => renderLink(item, currentPath === item.to))}
    </nav>
  );
}

/** Sidebar navigation for seller and admin (desktop-first, section 6.4). */
export function Sidebar({
  items,
  currentPath,
  renderLink,
  brand,
}: {
  items: NavItem[];
  currentPath: string;
  renderLink: (item: NavItem, isCurrent: boolean) => ReactNode;
  brand: ReactNode;
}) {
  return (
    <nav
      aria-label="Sections"
      className="bg-side text-on-dark wide:flex hidden w-60 shrink-0 flex-col gap-1 p-4"
    >
      <div className="px-2 pb-4">{brand}</div>
      {items.map((item) => renderLink(item, currentPath === item.to))}
    </nav>
  );
}
