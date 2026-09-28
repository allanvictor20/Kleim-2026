/** The fetch layer every app shares.
 *
 * Responsibilities the generated types cannot have: the base URL, attaching the
 * bearer token, refreshing it once when several requests hit 401 together,
 * carrying an `Idempotency-Key` across retries of one attempt, propagating
 * `X-Request-ID`, and turning any failure into an `ApiError`.
 */

import { ApiError, toApiError } from './errors';
import type { TokenPair, TokenStore } from './tokens';

export const REQUEST_ID_HEADER = 'X-Request-ID';
export const IDEMPOTENCY_HEADER = 'Idempotency-Key';

export interface FetcherOptions {
  baseUrl: string;
  tokens: TokenStore;
  /** Exchanges a refresh token for a new pair. M1 supplies the real call. */
  refresh?: (refreshToken: string) => Promise<TokenPair>;
  /** Called when refresh fails and the person must sign in again. */
  onSignedOut?: () => void;
  fetch?: typeof globalThis.fetch;
}

export interface RequestOptions {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  /** Reuse the same value across retries of one logical attempt (NFR-11). */
  idempotencyKey?: string;
  signal?: AbortSignal;
  headers?: Record<string, string>;
  /** Skip the bearer token, for the OTP endpoints and health checks. */
  anonymous?: boolean;
}

/** A fresh key per mutation attempt. Retrying that attempt reuses it, which is
 * what makes the retry safe: the backend replays the first response instead of
 * creating a second order (see backend/app/core/idempotency.py). */
export function newIdempotencyKey(): string {
  return crypto.randomUUID();
}

export class Fetcher {
  private readonly baseUrl: string;
  private readonly tokens: TokenStore;
  private readonly refreshFn: FetcherOptions['refresh'];
  private readonly onSignedOut: FetcherOptions['onSignedOut'];
  private readonly doFetch: typeof globalThis.fetch;
  /** The single in-flight refresh. Parallel 401s await this one promise, because
   * refresh tokens rotate on every use and the backend revokes the family when a
   * used token is presented again. */
  private refreshing: Promise<TokenPair | null> | null = null;

  constructor(options: FetcherOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, '');
    this.tokens = options.tokens;
    this.refreshFn = options.refresh;
    this.onSignedOut = options.onSignedOut;
    this.doFetch = options.fetch ?? globalThis.fetch.bind(globalThis);
  }

  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const response = await this.send(path, options);

    if (response.status === 401 && !options.anonymous && this.refreshFn) {
      const refreshed = await this.refreshOnce();
      if (refreshed) {
        return this.unwrap<T>(await this.send(path, options));
      }
    }

    return this.unwrap<T>(response);
  }

  private async send(path: string, options: RequestOptions): Promise<Response> {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      ...options.headers,
    };

    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    if (options.idempotencyKey) headers[IDEMPOTENCY_HEADER] = options.idempotencyKey;

    if (!options.anonymous) {
      const pair = this.tokens.get();
      if (pair) headers.Authorization = `Bearer ${pair.accessToken}`;
    }

    return this.doFetch(this.url(path, options.query), {
      method: options.method ?? 'GET',
      headers,
      ...(options.body !== undefined ? { body: JSON.stringify(options.body) } : {}),
      ...(options.signal ? { signal: options.signal } : {}),
    });
  }

  private url(path: string, query?: RequestOptions['query']): string {
    const url = new URL(`${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`);
    for (const [key, value] of Object.entries(query ?? {})) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
    return url.toString();
  }

  private async refreshOnce(): Promise<TokenPair | null> {
    this.refreshing ??= this.performRefresh().finally(() => {
      this.refreshing = null;
    });
    return this.refreshing;
  }

  private async performRefresh(): Promise<TokenPair | null> {
    const current = this.tokens.get();
    if (!current || !this.refreshFn) return null;
    try {
      const next = await this.refreshFn(current.refreshToken);
      this.tokens.set(next);
      return next;
    } catch {
      this.tokens.set(null);
      this.onSignedOut?.();
      return null;
    }
  }

  private async unwrap<T>(response: Response): Promise<T> {
    const requestId = response.headers.get(REQUEST_ID_HEADER);

    if (response.status === 204) return undefined as T;

    let body: unknown = null;
    const text = await response.text();
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = null;
      }
    }

    if (!response.ok) throw toApiError(response.status, body, requestId);
    return body as T;
  }
}

/** Convenience for the common case: a mutation that may be retried. */
export async function withIdempotency<T>(
  run: (key: string) => Promise<T>,
  key: string = newIdempotencyKey(),
): Promise<T> {
  return run(key);
}

export { ApiError };
