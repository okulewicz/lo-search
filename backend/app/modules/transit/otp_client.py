"""Open Trip Planner (OTP2) REST API transit provider."""

import httpx
from app.modules.transit.base import TransitProviderBase
from app.schemas.route import RouteRequest, RouteResponse, RouteItinerary, RouteLeg, Coordinate
from app.config import settings

# OTP2 GraphQL query for transit itineraries
_ITINERARY_QUERY = """
query Plan($fromLat: Float!, $fromLon: Float!, $toLat: Float!, $toLon: Float!, $dateTime: Long) {
  plan(
    from: {lat: $fromLat, lon: $fromLon}
    to:   {lat: $toLat,   lon: $toLon}
    numItineraries: 3
    transportModes: [{mode: TRANSIT}, {mode: WALK}]
    dateTime: $dateTime
  ) {
    itineraries {
      duration
      startTime
      endTime
      numberOfTransfers
      walkDistance
      legs {
        mode
        distance
        duration
        startTime
        endTime
        from { name lat lon }
        to   { name lat lon }
        route { shortName longName }
        headsign
      }
    }
  }
}
"""


class OTPTransitProvider(TransitProviderBase):
    """Connects to OTP2 via its GraphQL endpoint."""

    @property
    def graphql_url(self) -> str:
        # OTP2 GraphQL endpoint (adjust path if self-hosted OTP2 differs)
        base = settings.otp_base_url.rstrip("/")
        return f"{base.replace('/routers/default', '')}/otp/gtfs/v1"

    async def get_routes(self, request: RouteRequest) -> RouteResponse:
        variables = {
            "fromLat": request.from_lat,
            "fromLon": request.from_lon,
            "toLat": request.to_lat,
            "toLon": request.to_lon,
        }
        if request.departure_time:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(request.departure_time)
            variables["dateTime"] = int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                self.graphql_url,
                json={"query": _ITINERARY_QUERY, "variables": variables},
            )
            resp.raise_for_status()
            data = resp.json()

        raw_itineraries = data.get("data", {}).get("plan", {}).get("itineraries", [])
        itineraries = [self._parse_itinerary(it) for it in raw_itineraries]
        return RouteResponse(provider="otp", itineraries=itineraries)

    def _parse_itinerary(self, it: dict) -> RouteItinerary:
        legs = [self._parse_leg(l) for l in it.get("legs", [])]
        return RouteItinerary(
            duration_seconds=it["duration"],
            start_time=str(it["startTime"]),
            end_time=str(it["endTime"]),
            transfers=it.get("numberOfTransfers", 0),
            walk_distance_meters=it.get("walkDistance", 0.0),
            legs=legs,
        )

    def _parse_leg(self, leg: dict) -> RouteLeg:
        route = leg.get("route") or {}
        return RouteLeg(
            mode=leg["mode"],
            route_short_name=route.get("shortName"),
            headsign=leg.get("headsign"),
            from_name=leg["from"]["name"],
            to_name=leg["to"]["name"],
            from_coord=Coordinate(lat=leg["from"]["lat"], lon=leg["from"]["lon"]),
            to_coord=Coordinate(lat=leg["to"]["lat"], lon=leg["to"]["lon"]),
            distance_meters=leg["distance"],
            duration_seconds=leg["duration"],
            departure_time=str(leg.get("startTime")),
            arrival_time=str(leg.get("endTime")),
        )
