"""Image storage interface (M0). Cloudinary signed uploads arrive in M2.

Uploads are constrained by SDD section 21: jpg, png or webp only, at most 5 MB,
EXIF stripped, random storage key.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class UploadSignature:
    """Everything the client needs to upload straight to the provider."""

    url: str
    fields: dict[str, str]
    storage_key: str
    expires_in_seconds: int


class StorageClient(Protocol):
    def sign_upload(self, folder: str, content_type: str) -> UploadSignature:
        ...

    def public_url(self, storage_key: str, width: int | None = None) -> str:
        """Delivery URL, optionally width-transformed for low bandwidth (NFR-07)."""
        ...
