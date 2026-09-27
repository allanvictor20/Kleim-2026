"""Hashing and token primitives (M0).

M1 builds OTP login and the token pair on top of these; M0 only owns the
primitives so every module hashes and signs the same way.

OTP codes are hashed at rest with Argon2 -- a six-digit code has only a million
possibilities, so a leaked table of fast hashes would be trivially reversible.
"""
from __future__ import annotations

import hmac
import secrets
import string
import uuid
from datetime import timedelta
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from app.core.clock import now
from app.core.config import get_settings
from app.core.errors import Unauthorized

TokenType = Literal["access", "refresh"]

_hasher = PasswordHasher()

# Unambiguous alphabet for the 6-character public order code (Database Design
# section 2.2): no 0/O and no 1/I.
_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def hash_secret(secret: str) -> str:
    """Hash an OTP code, token or password."""
    return _hasher.hash(secret)


def verify_secret(hashed: str, secret: str) -> bool:
    """Constant-time verification that never raises on a mismatch."""
    try:
        return _hasher.verify(hashed, secret)
    except (VerifyMismatchError, VerificationError, ValueError):
        return False


def needs_rehash(hashed: str) -> bool:
    return _hasher.check_needs_rehash(hashed)


def numeric_code(length: int = 6) -> str:
    """Cryptographically random OTP code."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def public_code(length: int = 6) -> str:
    """Short human-readable code for orders and handovers."""
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))


def opaque_token(nbytes: int = 32) -> str:
    """Random string for a refresh token before it is hashed and stored."""
    return secrets.token_urlsafe(nbytes)


def constant_time_equals(left: str, right: str) -> bool:
    """For comparing webhook signatures (M6)."""
    return hmac.compare_digest(left.encode(), right.encode())


def create_token(
    subject: str,
    token_type: TokenType = "access",
    *,
    roles: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    """Sign a JWT whose lifetime comes from settings."""
    settings = get_settings()
    lifetime = (
        timedelta(minutes=settings.access_token_minutes)
        if token_type == "access"
        else timedelta(days=settings.refresh_token_days)
    )
    issued_at = now()
    claims: dict[str, Any] = {
        "sub": subject,
        "typ": token_type,
        "jti": str(uuid.uuid4()),
        "iat": issued_at,
        "exp": issued_at + lifetime,
    }
    if roles is not None:
        claims["roles"] = roles
    if extra:
        claims.update(extra)
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode and validate a JWT, raising `Unauthorized` on any problem."""
    settings = get_settings()
    try:
        claims: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise Unauthorized("Your session has expired", code="TOKEN_EXPIRED") from exc
    except jwt.PyJWTError as exc:
        raise Unauthorized("Invalid token") from exc
    if expected_type is not None and claims.get("typ") != expected_type:
        raise Unauthorized(f"Expected a {expected_type} token")
    return claims
