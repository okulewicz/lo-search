from fastapi import APIRouter, Depends
from app.schemas.route import RouteRequest, RouteResponse
from app.modules.transit.router import get_transit_provider

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/", response_model=RouteResponse)
async def plan_route(
    request: RouteRequest,
    provider=Depends(get_transit_provider),
):
    return await provider.get_routes(request)
