"""Audit schemas (M0). The admin-facing read endpoints arrive in M10."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_user_id: uuid.UUID | None
    action: str
    target_type: str
    target_id: uuid.UUID
    before: dict[str, Any] | None
    after: dict[str, Any] | None
    created_at: datetime
