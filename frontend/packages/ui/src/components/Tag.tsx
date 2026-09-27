/** Tag / badge — 11-12px bold, used for status and reasons.
 *
 * A status colour never stands alone (Style Guide section 4.1), so a Tag always
 * has text. Pink words use Pink 700, because Pink 500 fails contrast on white.
 */
import { clsx } from 'clsx';
import type { ReactNode } from 'react';
import type { Tone } from '@kleim/types';

export interface TagProps {
  tone?: Tone;
  children: ReactNode;
}

const TONES: Record<Tone, string> = {
  neutral: 'bg-chip text-muted',
  blue: 'bg-blue-soft text-link',
  green: 'bg-green-soft text-green',
  amber: 'bg-amber-soft text-amber',
  pink: 'bg-pink-soft text-pink-text',
};

export function Tag({ tone = 'neutral', children }: TagProps) {
  return (
    <span
      className={clsx(
        'rounded-pill text-caption inline-flex items-center px-2 py-0.5 font-bold',
        TONES[tone],
      )}
    >
      {children}
    </span>
  );
}
