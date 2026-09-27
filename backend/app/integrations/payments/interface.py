"""Payments adapter interface (M0). Implemented in M6; see ADR-003.

Money is integer UGX everywhere (ADR-002).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

PaymentStatus = Literal["pending", "succeeded", "failed"]
PaymentMethod = Literal["mtn_momo", "airtel_money", "cod"]


@dataclass(frozen=True)
class ChargeRequest:
    amount: int
    phone: str
    method: PaymentMethod
    reference: str


@dataclass(frozen=True)
class ChargeResult:
    status: PaymentStatus
    provider_reference: str
    message: str = ""


class PaymentsClient(Protocol):
    def charge(self, request: ChargeRequest) -> ChargeResult:
        """Start a collection. Terminal state usually arrives by webhook."""
        ...

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        ...
