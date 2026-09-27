"""Request-id middleware (M0).

Accepts an inbound `X-Request-ID` so a trace survives a proxy, otherwise mints
one. The id reaches log lines and every error body.
"""
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import reset_request_id, set_request_id

HEADER = "X-Request-ID"

Handler = Callable[[Request], Awaitable[Response]]


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        incoming = request.headers.get(HEADER, "").strip()
        request_id = incoming[:64] if incoming else str(uuid.uuid4())
        token = set_request_id(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            reset_request_id(token)
        response.headers[HEADER] = request_id
        response.headers["X-Response-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.1f}"
        return response
