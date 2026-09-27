/** Toast — top of screen, one line, four seconds, no action buttons.
 *
 * `role="status"` so it is announced without stealing focus (Style Guide section
 * 5). An action belongs in the screen, not in a message that disappears.
 */
import { clsx } from 'clsx';
import { useEffect, useState, type ReactNode } from 'react';
import type { Tone } from '@kleim/types';

const TONES: Record<Tone, string> = {
  neutral: 'bg-ink text-card',
  blue: 'bg-btn text-white',
  green: 'bg-green text-white',
  amber: 'bg-amber-soft text-amber',
  pink: 'bg-pink-soft text-pink-text',
};

export interface ToastProps {
  message: string;
  tone?: Tone;
  /** Style guide: four seconds. */
  durationMs?: number;
  onDismiss?: () => void;
}

export function Toast({ message, tone = 'neutral', durationMs = 4000, onDismiss }: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onDismiss?.();
    }, durationMs);
    return () => clearTimeout(timer);
  }, [durationMs, onDismiss]);

  if (!visible) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className={clsx(
        'fixed left-1/2 top-[calc(env(safe-area-inset-top,0px)+12px)] z-50 -translate-x-1/2',
        'text-small max-w-[calc(100%-36px)] rounded-md px-4 py-3 font-semibold',
        'shadow-[var(--shadow-raised)]',
        TONES[tone],
      )}
    >
      {message}
    </div>
  );
}

/** Minimal queue so a screen can raise a toast without owning the markup. */
export function ToastStack({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
