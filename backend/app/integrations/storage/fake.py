"""Local storage adapter (M0).

With no CLOUDINARY_URL set, development stores images locally, as the README
states. Keys are random so a URL cannot be guessed from a product id.
"""
from __future__ import annotations

import secrets

from app.core.config import get_settings
from app.integrations.storage.interface import (
    ALLOWED_CONTENT_TYPES,
    UploadSignature,
)

_EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


class LocalStorageClient:
    def sign_upload(self, folder: str, content_type: str) -> UploadSignature:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Unsupported image type: {content_type}")
        key = f"{folder}/{secrets.token_urlsafe(16)}.{_EXTENSIONS[content_type]}"
        base = get_settings().api_base_url.rstrip("/")
        return UploadSignature(
            url=f"{base}/api/v1/dev/uploads",
            fields={"key": key, "content_type": content_type},
            storage_key=key,
            expires_in_seconds=600,
        )

    def public_url(self, storage_key: str, width: int | None = None) -> str:
        base = get_settings().api_base_url.rstrip("/")
        url = f"{base}/media/{storage_key}"
        return f"{url}?w={width}" if width else url
