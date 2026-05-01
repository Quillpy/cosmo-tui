from __future__ import annotations
from dataclasses import dataclass
from .client import NasaClient

@dataclass
class MarsWeather:
    sol: int
    temp_min: float
    temp_max: float
    pressure: float
    opacity: str
    season: str
    atmo_temp: float

async def fetch_curiosity_weather(client: NasaClient) -> MarsWeather:
    """Fetch latest weather report from Curiosity rover (MAAS2 API)."""
    # Using MAAS2 API for Curiosity REMS data
    data = await client.get("https://api.maas2.apollorion.com/")
    if isinstance(data, dict):
        return MarsWeather(
            sol=int(data.get("sol", 0)),
            temp_min=float(data.get("min_temp", 0.0)),
            temp_max=float(data.get("max_temp", 0.0)),
            pressure=float(data.get("pressure", 0.0)),
            opacity=data.get("atmo_opacity", "Unknown"),
            season=data.get("season", "Unknown"),
            atmo_temp=float(data.get("atmo_temp", 0.0))
        )
    raise ValueError("Failed to fetch Mars weather data")
