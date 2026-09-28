/** The one error type screens handle. SDD section 15.1.
 *
 * Every failure from the API arrives as
 * `{"error": {"code", "message", "details", "request_id"}}`. This unwraps it so a
 * screen switches on `code` and never parses a message, and so the raw code
 * never reaches a person: Style Guide section 7.3 forbids showing error codes,
 * and `requestId` surfaces only behind "Contact support".
 */

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    request_id: string;
  };
}

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: Record<string, unknown> | undefined;
  /** Show only in "Contact support", never in the error message itself. */
  readonly requestId: string;

  constructor(args: {
    code: string;
    message: string;
    status: number;
    requestId: string;
    details?: Record<string, unknown>;
  }) {
    super(args.message);
    this.name = 'ApiError';
    this.code = args.code;
    this.status = args.status;
    this.requestId = args.requestId;
    this.details = args.details;
  }

  /** True when retrying the same request could plausibly succeed. */
  get isRetryable(): boolean {
    return this.status >= 500 || this.status === 429 || this.code === 'IDEMPOTENCY_IN_PROGRESS';
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (typeof value !== 'object' || value === null || !('error' in value)) return false;
  const error = (value as { error: unknown }).error;
  return (
    typeof error === 'object' &&
    error !== null &&
    typeof (error as { code?: unknown }).code === 'string' &&
    typeof (error as { message?: unknown }).message === 'string'
  );
}

/** Build an `ApiError` from a response body, whatever shape it turns out to be.
 *
 * A proxy, a gateway or a crash can return HTML or nothing at all, so this never
 * assumes the envelope is present.
 */
export function toApiError(
  status: number,
  body: unknown,
  requestIdHeader?: string | null,
): ApiError {
  if (isApiErrorBody(body)) {
    const { code, message, details, request_id } = body.error;
    return new ApiError({
      code,
      message,
      status,
      requestId: request_id || requestIdHeader || '-',
      ...(details ? { details } : {}),
    });
  }
  return new ApiError({
    code: status >= 500 ? 'INTERNAL_ERROR' : 'UNEXPECTED_RESPONSE',
    message: 'Something went wrong. Please try again.',
    status,
    requestId: requestIdHeader || '-',
  });
}
