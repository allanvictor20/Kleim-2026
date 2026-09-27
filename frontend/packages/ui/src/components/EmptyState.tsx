/** Empty state — heading, one sentence, one action (Style Guide sections 5, 7.3).
 *
 * Empty screens invite action: "No orders yet. Orders you place show up here with
 * live tracking." plus one button.
 */
import type { ReactNode } from 'react';

export interface EmptyStateProps {
  heading: string;
  /** One sentence. Never an apology, never a raw error code. */
  body: string;
  /** At most one. */
  action?: ReactNode;
}

export function EmptyState({ heading, body, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 px-[var(--screen-padding)] py-9 text-center">
      <h2 className="text-section text-ink">{heading}</h2>
      <p className="text-body text-muted max-w-[46ch]">{body}</p>
      {action ? <div className="w-full max-w-[280px] pt-2">{action}</div> : null}
    </div>
  );
}
