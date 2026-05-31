from typing import Optional
from pydantic import BaseModel


class Coordinate(BaseModel):
    lat: float
    lon: float


class RouteLeg(BaseModel):
    mode: str           # WALK, BUS, TRAM, SUBWAY, RAIL
    route_short_name: Optional[str] = None
    headsign: Optional[str] = None
    from_name: str
    to_name: str
    from_coord: Coordinate
    to_coord: Coordinate
    distance_meters: float
    duration_seconds: int
    departure_time: Optional[str] = None  # ISO8601
    arrival_time: Optional[str] = None


class RouteItinerary(BaseModel):
    duration_seconds: int
    start_time: str
    end_time: str
    transfers: int
    walk_distance_meters: float
    legs: list[RouteLeg]


class RouteRequest(BaseModel):
    from_lat: float
    from_lon: float
    to_lat: float
    to_lon: float
    departure_time: Optional[str] = None   # ISO8601; None = now


class RouteResponse(BaseModel):
    provider: str
    itineraries: list[RouteItinerary]
