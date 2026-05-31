from abc import ABC, abstractmethod
from app.schemas.route import RouteRequest, RouteResponse


class TransitProviderBase(ABC):
    """Common interface for all transit route providers."""

    @abstractmethod
    async def get_routes(self, request: RouteRequest) -> RouteResponse:
        """Return public transport itineraries between two coordinates."""
        ...
