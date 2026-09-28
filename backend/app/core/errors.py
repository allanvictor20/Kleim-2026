"""Domain errors and the single error response shape (M0).

Every failure leaving the API uses the envelope defined in SDD section 15.1 and
`docs/api/openapi.yaml` (`components.schemas.Error`)::

    {"error": {"code": ..., "message": ..., "details": ..., "request_id": ...}}

Routers and services raise these classes; they never build an error body by
hand (CONTRIBUTING.md section 5).
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.context import get_request_id

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for every error with a stable, documented code."""

    code = "INTERNAL_ERROR"
    status_code = 500
    message = "Something went wrong"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        if code is not None:
            self.code = code
        self.details = details
        super().__init__(self.message)


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 422
    message = "The request failed validation"


class Unauthorized(AppError):
    code = "UNAUTHORIZED"
    status_code = 401
    message = "Authentication is required"


class Forbidden(AppError):
    code = "FORBIDDEN"
    status_code = 403
    message = "You are not allowed to do this"


class NotFound(AppError):
    code = "NOT_FOUND"
    status_code = 404
    message = "Not found"


class Conflict(AppError):
    code = "CONFLICT"
    status_code = 409
    message = "The request conflicts with the current state"


class RateLimited(AppError):
    code = "RATE_LIMITED"
    status_code = 429
    message = "Too many requests"

    def __init__(
        self,
        message: str | None = None,
        *,
        retry_after_seconds: int | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)
        self.retry_after_seconds = retry_after_seconds


class BusinessRuleError(AppError):
    """A rule from the SDD refused the request, e.g. OUT_OF_STOCK.

    Always raised with an explicit code from the API Specification catalogue.
    """

    code = "BUSINESS_RULE_VIOLATED"
    status_code = 409
    message = "That is not allowed right now"


class ServiceUnavailable(AppError):
    code = "SERVICE_UNAVAILABLE"
    status_code = 503
    message = "A dependency is unavailable"


_STATUS_TO_CODE: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    503: "SERVICE_UNAVAILABLE",
}


def error_body(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the SDD section 15.1 envelope for one error."""
    error: dict[str, Any] = {"code": code, "message": message, "request_id": get_request_id()}
    if details is not None:
        error["details"] = details
    return {"error": error}


def _response(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_body(code, message, details),
        headers=headers,
    )


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    headers: dict[str, str] | None = None
    if isinstance(exc, RateLimited) and exc.retry_after_seconds is not None:
        headers = {"Retry-After": str(exc.retry_after_seconds)}
    return _response(exc.status_code, exc.code, exc.message, exc.details, headers)


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Wrap FastAPI's own validation failure so no ad-hoc body escapes."""
    assert isinstance(exc, RequestValidationError)
    fields = [
        {
            "field": ".".join(str(part) for part in err.get("loc", ()) if part != "body"),
            "message": err.get("msg", ""),
        }
        for err in exc.errors()
    ]
    return _response(422, ValidationError.code, ValidationError.message, {"fields": fields})


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = _STATUS_TO_CODE.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else code.replace("_", " ").title()
    headers = dict(exc.headers) if exc.headers else None
    return _response(exc.status_code, code, message, headers=headers)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last resort: log with the request id, return the same envelope."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _response(500, "INTERNAL_ERROR", "Something went wrong")


def register_exception_handlers(app: FastAPI) -> None:
    """Attach every handler so the error shape is identical across the API."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
