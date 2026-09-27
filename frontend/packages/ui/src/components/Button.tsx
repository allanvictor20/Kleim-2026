/** Button — UI/UX Style Guide section 5.
 *
 * At most one filled Kleim blue button per screen ("one clear action"), and the
 * label says what happens: "Place order", not "Submit".
 */
import { clsx } from 'clsx';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

import { Spinner } from './Spinner';

export type ButtonVariant = 'primary' | 'dark' | 'success' | 'outline' | 'text';

export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  variant?: ButtonVariant;
  /** Shows a spinner and blocks input without changing the button's width. */
  loading?: boolean;
  /** Full width is the default on phones; set false for inline actions. */
  fullWidth?: boolean;
  /** Rider actions are 54px high and sit in thumb reach (section 6.3). */
  size?: 'default' | 'rider';
  children: ReactNode;
}

const VARIANTS: Record<ButtonVariant, string> = {
  primary: 'bg-btn text-white border-transparent',
  dark: 'bg-ink text-card border-transparent',
  success: 'bg-green text-white border-transparent',
  outline: 'bg-transparent text-ink border-line',
  text: 'bg-transparent text-link border-transparent',
};

export function Button({
  variant = 'primary',
  loading = false,
  fullWidth = true,
  size = 'default',
  disabled,
  children,
  type = 'button',
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      // A loading button stays disabled so a double tap cannot place two orders.
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-md border font-bold',
        'text-body transition-[filter,opacity] active:brightness-95',
        'disabled:cursor-not-allowed disabled:opacity-50',
        size === 'rider' ? 'min-h-[var(--tap-rider)]' : 'min-h-[var(--button-height)]',
        fullWidth ? 'w-full px-5' : 'px-5',
        VARIANTS[variant],
      )}
      {...rest}
    >
      {loading ? <Spinner label="Working" /> : null}
      {children}
    </button>
  );
}
