import { describe, expect, it, vi, type Mock } from 'vitest';

import { ApiError } from './errors';
import { Fetcher, IDEMPOTENCY_HEADER, REQUEST_ID_HEADER, newIdempotencyKey } from './fetcher';
import { createTokenStore } from './tokens';

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json', [REQUEST_ID_HEADER]: 'req-1' },
    ...init,
  });
}

function errorResponse(status: number, code: string, message: string): Response {
  return new Response(JSON.stringify({ error: { code, message, request_id: 'req-err' } }), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

const BASE = 'http://localhost:8000/api/v1';

/** Read one recorded call. `noUncheckedIndexedAccess` is on, so index access is
 * narrowed here once rather than asserted in every test. */
function callOf(fetch: Mock, index: number): { url: string; init: RequestInit } {
  const call = fetch.mock.calls[index];
  if (!call) throw new Error(`fetch was not called ${index + 1} time(s)`);
  return { url: String(call[0]), init: (call[1] ?? {}) as RequestInit };
}

function headersOf(fetch: Mock, index: number): Record<string, string> {
  return (callOf(fetch, index).init.headers ?? {}) as Record<string, string>;
}

describe('Fetcher', () => {
  it('sends the bearer token when one is held', async () => {
    const tokens = createTokenStore();
    tokens.set({ accessToken: 'access-1', refreshToken: 'refresh-1' });
    const fetch = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));

    await new Fetcher({ baseUrl: BASE, tokens, fetch }).request('/me');

    expect(headersOf(fetch, 0).Authorization).toBe('Bearer access-1');
  });

  it('omits the token on an anonymous call', async () => {
    const tokens = createTokenStore();
    tokens.set({ accessToken: 'access-1', refreshToken: 'refresh-1' });
    const fetch = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));

    await new Fetcher({ baseUrl: BASE, tokens, fetch }).request('/auth/otp/request', {
      method: 'POST',
      anonymous: true,
      body: { phone: '+256700000001' },
    });

    expect(headersOf(fetch, 0).Authorization).toBeUndefined();
  });

  it('turns the SDD error envelope into a typed ApiError', async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(
        errorResponse(409, 'OUT_OF_STOCK', 'Selected size is no longer available'),
      );
    const fetcher = new Fetcher({ baseUrl: BASE, tokens: createTokenStore(), fetch });

    await expect(fetcher.request('/orders', { method: 'POST' })).rejects.toMatchObject({
      code: 'OUT_OF_STOCK',
      status: 409,
      requestId: 'req-err',
      message: 'Selected size is no longer available',
    });
  });

  it('still produces an ApiError when a proxy returns something else entirely', async () => {
    // A gateway can return HTML; the UI must not crash trying to read .error.
    const fetch = vi.fn().mockResolvedValue(new Response('<html>502</html>', { status: 502 }));
    const fetcher = new Fetcher({ baseUrl: BASE, tokens: createTokenStore(), fetch });

    const error = await fetcher.request('/products').catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).code).toBe('INTERNAL_ERROR');
    expect((error as ApiError).isRetryable).toBe(true);
  });

  it('refreshes once when several requests hit 401 together', async () => {
    // Refresh tokens rotate on every use and a reused one revokes the family, so
    // a burst of 401s must produce exactly one refresh.
    const tokens = createTokenStore();
    tokens.set({ accessToken: 'stale', refreshToken: 'refresh-1' });

    const fetch = vi.fn(async (_url: RequestInfo | URL, init?: RequestInit) => {
      const headers = (init?.headers ?? {}) as Record<string, string>;
      if (headers.Authorization === 'Bearer stale') {
        return errorResponse(401, 'UNAUTHORIZED', 'Authentication is required');
      }
      return jsonResponse({ ok: true });
    });

    const refresh = vi.fn().mockImplementation(async () => {
      await new Promise((resolve) => setTimeout(resolve, 5));
      return { accessToken: 'fresh', refreshToken: 'refresh-2' };
    });

    const fetcher = new Fetcher({ baseUrl: BASE, tokens, fetch, refresh });
    const results = await Promise.all([
      fetcher.request('/me'),
      fetcher.request('/me/addresses'),
      fetcher.request('/customer/orders'),
    ]);

    expect(refresh).toHaveBeenCalledTimes(1);
    expect(results).toHaveLength(3);
    expect(tokens.get()?.accessToken).toBe('fresh');
  });

  it('signs the person out when the refresh itself fails', async () => {
    const tokens = createTokenStore();
    tokens.set({ accessToken: 'stale', refreshToken: 'used-already' });
    const fetch = vi.fn().mockResolvedValue(errorResponse(401, 'UNAUTHORIZED', 'Invalid token'));
    const onSignedOut = vi.fn();
    const refresh = vi.fn().mockRejectedValue(new Error('token reused'));

    const fetcher = new Fetcher({ baseUrl: BASE, tokens, fetch, refresh, onSignedOut });
    await expect(fetcher.request('/me')).rejects.toBeInstanceOf(ApiError);

    expect(onSignedOut).toHaveBeenCalledOnce();
    expect(tokens.get()).toBeNull();
  });

  it('holds one Idempotency-Key across retries of the same attempt', async () => {
    // This is what makes a retry safe: the backend replays the first response
    // rather than creating a second order (NFR-11).
    const key = newIdempotencyKey();
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(errorResponse(503, 'SERVICE_UNAVAILABLE', 'Try again'))
      .mockResolvedValueOnce(jsonResponse({ id: 'order-1' }, { status: 201 }));
    const fetcher = new Fetcher({ baseUrl: BASE, tokens: createTokenStore(), fetch });

    await fetcher
      .request('/orders', { method: 'POST', idempotencyKey: key })
      .catch(() => undefined);
    await fetcher.request('/orders', { method: 'POST', idempotencyKey: key });

    expect(headersOf(fetch, 0)[IDEMPOTENCY_HEADER]).toBe(key);
    expect(headersOf(fetch, 1)[IDEMPOTENCY_HEADER]).toBe(key);
  });

  it('mints a distinct key per attempt', () => {
    expect(newIdempotencyKey()).not.toBe(newIdempotencyKey());
  });

  it('builds query strings and drops undefined filters', async () => {
    const fetch = vi.fn().mockResolvedValue(jsonResponse({ items: [] }));
    await new Fetcher({ baseUrl: BASE, tokens: createTokenStore(), fetch }).request('/products', {
      query: { occasion: 'wedding', size: undefined, max_price: 120000 },
    });

    const { url } = callOf(fetch, 0);
    expect(url).toContain('occasion=wedding');
    expect(url).toContain('max_price=120000');
    expect(url).not.toContain('size=');
  });

  it('handles 204 with no body', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    const result = await new Fetcher({ baseUrl: BASE, tokens: createTokenStore(), fetch }).request(
      '/me/favorites/abc',
      { method: 'DELETE' },
    );
    expect(result).toBeUndefined();
  });
});

describe('token store', () => {
  it('tells subscribers when the pair changes', () => {
    const tokens = createTokenStore();
    const listener = vi.fn();
    const unsubscribe = tokens.subscribe(listener);

    tokens.set({ accessToken: 'a', refreshToken: 'b' });
    unsubscribe();
    tokens.set(null);

    expect(listener).toHaveBeenCalledTimes(1);
  });
});
