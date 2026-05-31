"""Google Maps Directions API transit provider."""

import httpx
from datetime import datetime, timezone

from app.modules.transit.base import TransitProviderBase
from app.schemas.route import RouteRequest, RouteResponse, RouteItinerary, RouteLeg, Coordinate
from app.config import settings


class GoogleMapsTransitProvider(TransitProviderBase):
    BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

    async def get_routes(self, request: RouteRequest) -> RouteResponse:
        departure_time = "now"
        if request.departure_time:
            dt = datetime.fromisoformat(request.departure_time)
            departure_time = int(dt.replace(tzinfo=timezone.utc).timestamp())

        params = {
            "origin": f"{request.from_lat},{request.from_lon}",
            "destination": f"{request.to_lat},{request.to_lon}",
            "mode": "transit",
            "departure_time": departure_time,
            "alternatives": "true",
            "language": "pl",
            "key": settings.google_maps_api_key,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        itineraries = [self._parse_route(r) for r in data.get("routes", [])]
        return RouteResponse(provider="google_maps", itineraries=itineraries)

    def _parse_route(self, route: dict) -> RouteItinerary:
        leg_data = route["legs"][0]
        legs = [self._parse_step(s) for s in leg_data.get("steps", [])]
        return RouteItinerary(
            duration_seconds=leg_data["duration"]["value"],
            start_time=leg_data.get("departure_time", {}).get("text", ""),
            end_time=leg_data.get("arrival_time", {}).get("text", ""),
            transfers=sum(1 for l in legs if l.mode not in ("WALK",)) - 1,
            walk_distance_meters=sum(
                l.distance_meters for l in legs if l.mode == "WALK"
            ),
            legs=legs,
        )

    def _parse_step(self, step: dict) -> RouteLeg:
        transit = step.get("transit_details", {})
        line = transit.get("line", {})
        mode = step.get("travel_mode", "WALK")
        if mode == "TRANSIT":
            vehicle = line.get("vehicle", {}).get("type", "BUS")
            mode = vehicle

        return RouteLeg(
            mode=mode,
            route_short_name=line.get("short_name"),
            headsign=transit.get("headsign"),
            from_name=transit.get("departure_stop", {}).get("name", ""),
            to_name=transit.get("arrival_stop", {}).get("name", ""),
            from_coord=Coordinate(
                lat=step["start_location"]["lat"],
                lon=step["start_location"]["lng"],
            ),
            to_coord=Coordinate(
                lat=step["end_location"]["lat"],
                lon=step["end_location"]["lng"],
            ),
            distance_meters=step["distance"]["value"],
            duration_seconds=step["duration"]["value"],
            departure_time=transit.get("departure_time", {}).get("text"),
            arrival_time=transit.get("arrival_time", {}).get("text"),
        )
