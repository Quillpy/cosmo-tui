from __future__ import annotations
from dataclasses import dataclass
from .client import NasaClient

@dataclass
class Location:
    lat: float
    lon: float
    city: str
    country: str

async def fetch_user_location(client: NasaClient) -> Location:
    """Fetch user's latitude and longitude based on IP address."""
    # Using ip-api.com (free, no key required for non-commercial use)
    data = await client.get("http://ip-api.com/json/")
    if isinstance(data, dict) and data.get("status") == "success":
        return Location(
            lat=float(data.get("lat", 0.0)),
            lon=float(data.get("lon", 0.0)),
            city=data.get("city", "Unknown"),
            country=data.get("country", "Unknown")
        )
    raise ValueError("Failed to fetch geolocation data")
