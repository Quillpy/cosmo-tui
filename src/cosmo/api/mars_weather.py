from __future__ import annotations
from dataclasses import dataclass
from .client import NasaClient

@dataclass
class MarsWeather:
    sol: int
    temp_min: float
    temp_max: float
    pressure: float
    atmo_opacity: str
    season: str
    terrestrial_date: str

async def fetch_curiosity_weather(client: NasaClient) -> MarsWeather:
    """Fetch latest weather report from Curiosity (MSL) via NASA's RSS API."""
    # Using the MSL weather feed from mars.nasa.gov
    data = await client.get(
        "https://mars.nasa.gov/rss/api/",
        params={"feed": "weather", "category": "msl", "feedtype": "json"},
    )
    if not isinstance(data, dict):
        raise ValueError("Failed to fetch Mars weather data")

    soles = data.get("soles") or []
    if not soles:
        raise ValueError("No Mars weather soles available")

    # Get the latest sol
    sol_data = soles[0]

    def to_float(val: object) -> float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def to_int(val: object) -> int:
        try:
            return int(val)
        except (ValueError, TypeError):
            return 0

    return MarsWeather(
        sol=to_int(sol_data.get("sol", 0)),
        temp_min=to_float(sol_data.get("min_temp", "0")),
        temp_max=to_float(sol_data.get("max_temp", "0")),
        pressure=to_float(sol_data.get("pressure", "0")),
        atmo_opacity=sol_data.get("atmo_opacity", "Unknown"),
        season=sol_data.get("season", "Unknown"),
        terrestrial_date=sol_data.get("terrestrial_date", "Unknown"),
    )
