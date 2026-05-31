"""Factory that returns the configured transit provider."""

from functools import lru_cache
from app.config import settings
from app.modules.transit.base import TransitProviderBase


@lru_cache(maxsize=1)
def get_transit_provider() -> TransitProviderBase:
    if settings.transit_provider == "google_maps":
        from app.modules.transit.google_maps import GoogleMapsTransitProvider
        return GoogleMapsTransitProvider()
    from app.modules.transit.otp_client import OTPTransitProvider
    return OTPTransitProvider()
