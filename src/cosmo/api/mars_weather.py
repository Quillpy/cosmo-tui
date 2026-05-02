from __future__ import annotations
from dataclasses import dataclass
from .client import NasaClient

@dataclass
class MarsWeather:
    sol: int
    temp_min: float
    temp_max: float
    pressure: float
    wind_direction: str
    season: str
    atmo_temp: float

async def fetch_curiosity_weather(client: NasaClient) -> MarsWeather:
    """Fetch latest weather report from NASA's InSight Mars weather API."""
    data = await client.get(
        "https://api.nasa.gov/insight_weather/",
        params={"feedtype": "json", "ver": "1.0"},
    )
    if not isinstance(data, dict):
        raise ValueError("Failed to fetch Mars weather data")

    sol_keys = data.get("sol_keys") or []
    if not sol_keys:
        raise ValueError("No Mars weather sols available")

    sol = sol_keys[-1]
    sol_data = data.get(sol) or {}
    at = sol_data.get("AT") or {}
    pre = sol_data.get("PRE") or {}
    wd = sol_data.get("WD") or {}
    most_common = wd.get("most_common") or {}

    return MarsWeather(
        sol=int(sol),
        temp_min=float(at.get("mn", 0.0)),
        temp_max=float(at.get("mx", 0.0)),
        pressure=float(pre.get("av", 0.0)),
        wind_direction=most_common.get("compass_point", "Unknown"),
        season=sol_data.get("Season", "Unknown"),
        atmo_temp=float(at.get("av", 0.0)),
    )
