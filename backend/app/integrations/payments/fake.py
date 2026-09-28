"""Simulated payments adapter (M0).

The MVP does not move live money (SDD section 2.2): payments stay in simulated
states and an operator drives the outcome from the admin Dev Payments page
(`POST /api/v1/dev/payments/{id}/simulate`, added in M6). Charges therefore
settle as `pending` here and are resolved explicitly.
"""
from __future__ import annotations

import logging

from app.core.security import public_code
from app.integrations.payments.interface import ChargeRequest, ChargeResult

logger = logging.getLogger("kleim.payments")


class SimulatedPaymentsClient:
    def __init__(self) -> None:
        self.charges: list[ChargeRequest] = []

    def charge(self, request: ChargeRequest) -> ChargeResult:
        self.charges.append(request)
        reference = f"sim-{public_code(8)}"
        logger.info(
            "simulated charge accepted",
            extra={"amount": request.amount, "method": request.method, "reference": reference},
        )
        return ChargeResult(
            status="pending",
            provider_reference=reference,
            message="Awaiting simulated confirmation",
        )

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        # The simulator signs nothing; M6 enforces a real signature.
        return True

    def clear(self) -> None:
        self.charges.clear()
