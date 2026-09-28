"""Choose the storage adapter from settings (M0)."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.integrations.storage.fake import LocalStorageClient
from app.integrations.storage.interface import StorageClient


@lru_cache(maxsize=1)
def get_storage_client() -> StorageClient:
    if not get_settings().cloudinary_url:
        return LocalStorageClient()
    raise NotImplementedError("Cloudinary adapter is implemented in M2")


def reset_storage_client() -> None:
    get_storage_client.cache_clear()
