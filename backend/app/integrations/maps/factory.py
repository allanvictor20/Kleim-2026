"""Choose the maps adapter from settings (M0). See ADR-011."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.integrations.maps.fake import StraightLineMapsClient
from app.integrations.maps.interface import MapsClient


@lru_cache(maxsize=1)
def get_maps_client() -> MapsClient:
    settings = get_settings()
    if settings.maps_provider == "osm":
        return StraightLineMapsClient()
    if settings.maps_provider == "google":
        raise NotImplementedError("Google Maps adapter is implemented in M4 (see ADR-011)")
    raise ValueError(f"Unknown MAPS_PROVIDER: {settings.maps_provider}")


def reset_maps_client() -> None:
    get_maps_client.cache_clear()
