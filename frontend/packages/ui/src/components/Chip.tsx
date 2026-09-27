/** Chip — filter, soft and occasion variants (Style Guide section 5).
 *
 * Chips live in horizontal scroll rows and never wrap to a second line.
 */
import { clsx } from 'clsx';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface ChipProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  selected?: boolean;
  children: ReactNode;
}

export function Chip({ selected = false, children, type = 'button', ...rest }: ChipProps) {
  return (
    <button
      type={type}
      // aria-pressed, not a class alone: selection must reach a screen reader.
      aria-pressed={selected}
      className={clsx(
        'rounded-pill inline-flex min-h-[var(--tap)] shrink-0 items-center border px-4',
        'text-small whitespace-nowrap font-semibold',
        selected ? 'bg-blue-soft border-link text-link' : 'bg-chip border-line text-ink',
      )}
      {...rest}
    >
      {children}
    </button>
  );
}

/** A single-line, horizontally scrolling row of chips. */
export function ChipRow({ children, label }: { children: ReactNode; label: string }) {
  return (
    <div
      role="group"
      aria-label={label}
      className="flex gap-2 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      {children}
    </div>
  );
}
