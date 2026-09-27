/** Access and refresh token storage.
 *
 * In memory only: CONTRIBUTING.md section 5 forbids `localStorage` for anything
 * sensitive, and a token in local storage is readable by any script that gets
 * injected into the page. A reload therefore signs the person out until M1 adds
 * a refresh cookie, which is the correct trade for a marketplace holding
 * addresses and payment prompts.
 */

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

export interface TokenStore {
  get(): TokenPair | null;
  set(tokens: TokenPair | null): void;
  subscribe(listener: (tokens: TokenPair | null) => void): () => void;
}

export function createTokenStore(): TokenStore {
  let tokens: TokenPair | null = null;
  const listeners = new Set<(tokens: TokenPair | null) => void>();

  return {
    get: () => tokens,
    set(next) {
      tokens = next;
      for (const listener of listeners) listener(next);
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}
