"""Straight-line maps adapter (M0).

Development default. Uses the haversine distance x 1.3, which is the fallback
the SDD prescribes when a provider is unavailable, so local pricing is realistic
without an API key.
"""
from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from app.integrations.maps.interface import Point, Route

EARTH_RADIUS_METRES = 6_371_000
ROAD_FACTOR = 1.3
ASSUMED_SPEED_METRES_PER_SECOND = 7.0  # roughly 25 km/h through Kampala traffic


def haversine_metres(origin: Point, destination: Point) -> int:
    lon1, lat1, lon2, lat2 = (
        radians(origin.longitude),
        radians(origin.latitude),
        radians(destination.longitude),
        radians(destination.latitude),
    )
    d_lat, d_lon = lat2 - lat1, lon2 - lon1
    h = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return round(2 * EARTH_RADIUS_METRES * asin(sqrt(h)))


class StraightLineMapsClient:
    def route(self, origin: Point, destination: Point) -> Route:
        straight = haversine_metres(origin, destination)
        distance = round(straight * ROAD_FACTOR)
        return Route(
            distance_metres=distance,
            duration_seconds=round(distance / ASSUMED_SPEED_METRES_PER_SECOND),
            estimated=True,
        )
