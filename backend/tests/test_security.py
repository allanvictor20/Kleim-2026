"""Hashing and token primitives (M1 builds OTP login on these)."""
from __future__ import annotations

import pytest

from app.core import security
from app.core.config import get_settings
from app.core.errors import Unauthorized


def test_a_secret_hashes_differently_every_time_but_verifies() -> None:
    first = security.hash_secret("123456")
    second = security.hash_secret("123456")

    assert first != second
    assert security.verify_secret(first, "123456")


def test_a_wrong_secret_returns_false_rather_than_raising() -> None:
    hashed = security.hash_secret("123456")

    assert security.verify_secret(hashed, "654321") is False
    assert security.verify_secret("not-a-hash", "123456") is False


def test_otp_codes_are_six_digits() -> None:
    code = security.numeric_code()
    assert len(code) == 6
    assert code.isdigit()


def test_public_codes_avoid_ambiguous_characters() -> None:
    """Database Design section 2.2: customers read these over the phone."""
    codes = "".join(security.public_code() for _ in range(200))
    assert not set(codes) & set("01OI")


def test_tokens_round_trip_with_their_type_and_roles() -> None:
    settings = get_settings()
    token = security.create_token("user-1", "access", roles=["customer", "seller"])

    claims = security.decode_token(token, expected_type="access")

    assert claims["sub"] == "user-1"
    assert claims["roles"] == ["customer", "seller"]
    assert claims["jti"]
    assert settings.jwt_algorithm == "HS256"


def test_a_refresh_token_is_not_accepted_as_an_access_token() -> None:
    refresh = security.create_token("user-1", "refresh")

    with pytest.raises(Unauthorized):
        security.decode_token(refresh, expected_type="access")


def test_a_tampered_token_is_rejected() -> None:
    token = security.create_token("user-1")

    with pytest.raises(Unauthorized):
        security.decode_token(token[:-4] + "aaaa")


def test_each_token_has_a_unique_id_so_a_reused_refresh_can_be_detected() -> None:
    """M1 rotates refresh tokens and revokes a reused one; that needs a jti."""
    first = security.decode_token(security.create_token("user-1", "refresh"))
    second = security.decode_token(security.create_token("user-1", "refresh"))

    assert first["jti"] != second["jti"]
