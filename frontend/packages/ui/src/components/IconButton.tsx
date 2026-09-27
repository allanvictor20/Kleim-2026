/** Icon button — 44px round, always labelled (Style Guide sections 5 and 8). */
import { clsx } from 'clsx';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface IconButtonProps extends Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  'className' | 'aria-label'
> {
  /** Required: an icon alone tells a screen reader nothing. */
  label: string;
  /** Small count shown on the corner, e.g. unread notifications. */
  badge?: number;
  children: ReactNode;
}

export function IconButton({ label, badge, children, type = 'button', ...rest }: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      className={clsx(
        'relative inline-flex h-[var(--tap)] w-[var(--tap)] items-center justify-center',
        'rounded-pill text-ink disabled:opacity-50',
      )}
      {...rest}
    >
      {children}
      {badge !== undefined && badge > 0 ? (
        <span
          // Pink is the accent for badge counters (section 4.1).
          className="bg-pink rounded-pill text-caption absolute right-0 top-0 min-w-4 px-1 font-bold text-white"
        >
          {badge > 99 ? '99+' : badge}
        </span>
      ) : null}
    </button>
  );
}
