import { EmptyState } from '@kleim/ui';
import { Link } from 'react-router';

/** Style Guide section 7.3: say what happened and offer the way out. */
export function NotFound() {
  return (
    <EmptyState
      heading="This page does not exist"
      body="The link may be out of date. Go back to the start and try again."
      action={
        <Link
          to="/"
          className="border-line text-body text-ink inline-flex min-h-[var(--button-height)] w-full items-center justify-center rounded-md border px-5 font-bold"
        >
          Go to the start
        </Link>
      }
    />
  );
}
