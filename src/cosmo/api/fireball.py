from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .client import NasaClient

FIREBALL_URL = "https://ssd-api.jpl.nasa.gov/fireball.api"


@dataclass
class Fireball:
    date: str
    lat: float
    lon: float
    energy_kt: float  # total radiated energy in kilotons
    impact_energy_kt: float
    velocity_kms: float


async def fetch_fireballs(client: NasaClient, days: int = 365) -> list[Fireball]:
    """Fetch recent fireball atmospheric impact events."""
    end = date.today()
    start = end - timedelta(days=days)
    data = await client.get(
        FIREBALL_URL,
        params={
            "date-min": start.isoformat(),
            "date-max": end.isoformat(),
            "req-loc": "true",  # only fireballs with location data
        },
    )
    results: list[Fireball] = []
    fields = data.get("fields", [])
    rows = data.get("data", [])
    if not fields or not rows:
        return results

    # Build index map for field positions
    idx = {name: i for i, name in enumerate(fields)}

    for row in rows:
        try:
            lat_val = float(row[idx["lat"]])
            lat_dir = row[idx["lat-dir"]]
            lon_val = float(row[idx["lon"]])
            lon_dir = row[idx["lon-dir"]]

            lat = lat_val if lat_dir == "N" else -lat_val
            lon = lon_val if lon_dir == "E" else -lon_val

            energy = float(row[idx["energy"]]) if row[idx["energy"]] else 0.0
            impact_e = float(row[idx["impact-e"]]) if row[idx["impact-e"]] else 0.0
            vel = float(row[idx["vel"]]) if row[idx["vel"]] else 0.0

            results.append(Fireball(
                date=row[idx["date"]] or "",
                lat=lat,
                lon=lon,
                energy_kt=energy,
                impact_energy_kt=impact_e,
                velocity_kms=vel,
            ))
        except (KeyError, IndexError, TypeError, ValueError):
            continue

    results.sort(key=lambda f: f.date, reverse=True)
    return results
