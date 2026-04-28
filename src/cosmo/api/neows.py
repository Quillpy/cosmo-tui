from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .client import NasaClient

NEOWS_URL = "https://api.nasa.gov/neo/rest/v1/feed"


@dataclass
class Neo:
    name: str
    date: str
    diameter_min_m: float
    diameter_max_m: float
    miss_km: float
    miss_lunar: float
    velocity_kms: float
    hazardous: bool


async def fetch_neos(client: NasaClient, days: int = 7) -> list[Neo]:
    today = date.today()
    end = today + timedelta(days=min(days, 7))
    data = await client.get(
        NEOWS_URL,
        params={"start_date": today.isoformat(), "end_date": end.isoformat()},
    )
    results: list[Neo] = []
    for day, objs in (data.get("near_earth_objects") or {}).items():
        for o in objs:
            try:
                diam = o["estimated_diameter"]["meters"]
                ca = o["close_approach_data"][0]
                results.append(
                    Neo(
                        name=o.get("name", "?"),
                        date=ca.get("close_approach_date_full") or ca.get("close_approach_date") or day,
                        diameter_min_m=float(diam["estimated_diameter_min"]),
                        diameter_max_m=float(diam["estimated_diameter_max"]),
                        miss_km=float(ca["miss_distance"]["kilometers"]),
                        miss_lunar=float(ca["miss_distance"]["lunar"]),
                        velocity_kms=float(ca["relative_velocity"]["kilometers_per_second"]),
                        hazardous=bool(o.get("is_potentially_hazardous_asteroid", False)),
                    )
                )
            except (KeyError, IndexError, ValueError, TypeError):
                continue
    results.sort(key=lambda n: n.date)
    return results
