/** Skeleton — placeholder while content loads.
 *
 * Decorative: it carries `aria-hidden`, and the surrounding region announces
 * loading, so a screen reader is not read a wall of empty boxes.
 */
import { clsx } from 'clsx';

export interface SkeletonProps {
  /** Tailwind height class, e.g. `h-4`. */
  height?: string;
  width?: string;
  rounded?: 'sm' | 'md' | 'pill';
}

export function Skeleton({ height = 'h-4', width = 'w-full', rounded = 'sm' }: SkeletonProps) {
  return (
    <span
      aria-hidden="true"
      className={clsx(
        'bg-chip block animate-pulse',
        height,
        width,
        rounded === 'pill' ? 'rounded-pill' : rounded === 'md' ? 'rounded-md' : 'rounded-sm',
      )}
    />
  );
}
