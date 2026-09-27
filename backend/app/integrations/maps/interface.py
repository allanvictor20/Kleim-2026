"""Maps adapter interface (M0). Road distance for delivery pricing (M4)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Point:
    """WGS84 coordinate. Longitude first, matching geography(Point, 4326)."""

    longitude: float
    latitude: float


@dataclass(frozen=True)
class Route:
    distance_metres: int
    duration_seconds: int
    # True when the provider could not give a road distance and the caller got
    # the straight-line fallback (SDD section 14: straight line x 1.3).
    estimated: bool = False


class MapsClient(Protocol):
    def route(self, origin: Point, destination: Point) -> Route:
        ...
