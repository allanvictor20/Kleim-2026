/** The app's single API client.
 *
 * Tokens live in memory only (CONTRIBUTING.md section 5). M1 replaces the
 * `refresh` stub with the real `POST /auth/refresh` call.
 */
import { createClient, createTokenStore } from '@kleim/api-client';

export const tokens = createTokenStore();

export const api = createClient({
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  tokens,
});
