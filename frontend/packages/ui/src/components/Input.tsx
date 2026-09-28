/** Input — text, search and code entry (Style Guide section 5).
 *
 * Every input has a real <label>. Error text sits below the field in Pink 700 and
 * starts with what to do: "That code doesn't match. Ask the store to read it
 * again." — never a raw error code (section 7.3).
 */
import { clsx } from 'clsx';
import { useId, type InputHTMLAttributes } from 'react';

export interface InputProps extends Omit<
  InputHTMLAttributes<HTMLInputElement>,
  'className' | 'id'
> {
  label: string;
  /** Hide the label visually where the placement already makes it obvious. */
  hideLabel?: boolean;
  error?: string;
  hint?: string;
  /** `code` gives large tabular digits and a numeric keypad for handover codes. */
  variant?: 'text' | 'search' | 'code';
}

export function Input({
  label,
  hideLabel = false,
  error,
  hint,
  variant = 'text',
  ...rest
}: InputProps) {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  const describedBy = [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(' ');

  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={id}
        className={clsx(
          'text-small text-ink font-bold',
          hideLabel && 'sr-only absolute h-px w-px overflow-hidden',
        )}
      >
        {label}
      </label>
      <input
        id={id}
        type={variant === 'search' ? 'search' : 'text'}
        // A numeric keypad for codes: riders type these one-handed (section 6.3).
        inputMode={variant === 'code' ? 'numeric' : undefined}
        autoComplete={variant === 'code' ? 'one-time-code' : rest.autoComplete}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy || undefined}
        className={clsx(
          'bg-card text-ink min-h-[var(--tap)] rounded-md border px-3',
          variant === 'code'
            ? 'text-code text-center font-extrabold [font-variant-numeric:tabular-nums]'
            : 'text-body',
          error ? 'border-pink' : 'border-line',
        )}
        {...rest}
      />
      {hint ? (
        <p id={hintId} className="text-small text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-pink-text text-small font-semibold">
          {error}
        </p>
      ) : null}
    </div>
  );
}
