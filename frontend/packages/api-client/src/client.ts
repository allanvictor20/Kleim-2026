/** The app-facing client.
 *
 * Paths and response shapes come from `src/generated/schema.d.ts`, generated from
 * `docs/api/openapi.yaml`. Only the handful of calls M0 needs are wrapped here;
 * each module adds its own as it lands, so the wrapper never drifts ahead of the
 * contract.
 */

import { Fetcher, type FetcherOptions } from './fetcher';

export interface HealthReport {
  status: string;
  checks?: Record<string, string>;
}

export class KleimClient {
  readonly http: Fetcher;
  private readonly baseUrl: string;

  constructor(options: FetcherOptions) {
    this.http = new Fetcher(options);
    this.baseUrl = options.baseUrl.replace(/\/$/, '');
  }

  /** Readiness, used by each app shell to show whether the API is reachable.
   *
   * `/health/ready` sits outside the `/api/v1` prefix, so it is addressed from
   * the origin rather than the API base path.
   */
  async health(signal?: AbortSignal): Promise<HealthReport> {
    const origin = new URL(this.baseUrl).origin;
    const response = await fetch(`${origin}/health/ready`, signal ? { signal } : {});
    const body = (await response.json()) as HealthReport | { error: unknown };
    if (!response.ok && 'error' in body) {
      // Ready returns 503 with the standard envelope when a dependency is down;
      // that is a report, not an exception, so hand back the checks.
      const details = (body as { error: { details?: { checks?: Record<string, string> } } }).error
        .details;
      return { status: 'unavailable', ...(details?.checks ? { checks: details.checks } : {}) };
    }
    return body as HealthReport;
  }
}

export function createClient(options: FetcherOptions): KleimClient {
  return new KleimClient(options);
}

/** `VITE_API_BASE_URL`, or the local API the README documents. */
export function defaultBaseUrl(env: Record<string, string | undefined> = {}): string {
  return env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
}
