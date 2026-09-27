/** Error boundary — the last thing between a bug and a blank screen.
 *
 * Copy follows Style Guide section 7.3: say what happened and how to fix it,
 * never blame the person, never show a raw error code. The request id appears
 * only under "Contact support", which is why it sits behind a <details>.
 */
import { Component, type ErrorInfo, type ReactNode } from 'react';

import { Button } from './Button';
import { EmptyState } from './EmptyState';

export interface ErrorBoundaryProps {
  children: ReactNode;
  /** Sentry or another reporter; wired per app. */
  onError?: (error: Error, info: ErrorInfo) => void;
}

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, State> {
  override state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    this.props.onError?.(error, info);
  }

  private readonly retry = (): void => {
    this.setState({ error: null });
  };

  override render(): ReactNode {
    const { error } = this.state;
    if (!error) return this.props.children;

    // `requestId` is present when the failure came from the API client.
    const requestId = (error as { requestId?: string }).requestId;

    return (
      <div role="alert">
        <EmptyState
          heading="This screen did not load"
          body="Something on our side went wrong. Try again, and if it keeps happening, contact support."
          action={<Button onClick={this.retry}>Try again</Button>}
        />
        {requestId ? (
          <details className="text-muted text-small px-[var(--screen-padding)] pb-6 text-center">
            <summary className="cursor-pointer">Contact support</summary>
            <p className="pt-2">
              Quote reference <code>{requestId}</code> so support can find what happened.
            </p>
          </details>
        ) : null}
      </div>
    );
  }
}
