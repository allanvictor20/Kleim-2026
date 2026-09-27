import { EmptyState, Tag } from '@kleim/ui';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router';

import { api } from '../lib/api';

/** The M0 shell.
 *
 * It calls the API so "all four frontend apps load their empty shells against
 * the local API" -- the module's exit criterion -- is demonstrable rather than
 * asserted. Real screens arrive with their modules.
 */
export function Landing() {
  const health = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => api.health(signal),
  });

  const tone = health.isPending ? 'neutral' : health.data?.status === 'ok' ? 'green' : 'pink';
  const label = health.isPending
    ? 'Checking the API'
    : health.data?.status === 'ok'
      ? 'API reachable'
      : 'API unreachable';

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Tag tone={tone}>{label}</Tag>
        {health.data?.checks
          ? Object.entries(health.data.checks).map(([name, state]) => (
              <Tag key={name} tone={state === 'ok' ? 'green' : 'pink'}>
                {name} {state}
              </Tag>
            ))
          : null}
      </div>

      <EmptyState
        heading="No job right now"
        body="Go online and offers appear here. Delivery jobs arrive with M7."
        action={
          <Link
            to="/preview"
            className="bg-btn text-body inline-flex min-h-[var(--button-height)] w-full items-center justify-center rounded-md px-5 font-bold text-white"
          >
            View the component set
          </Link>
        }
      />
    </div>
  );
}
