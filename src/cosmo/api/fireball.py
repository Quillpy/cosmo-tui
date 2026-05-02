from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
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
            "req-vel-comp": "true",
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
            lat_raw = row[idx["lat"]]
            lon_raw = row[idx["lon"]]
            lat_dir = row[idx["lat-dir"]]
            lon_dir = row[idx["lon-dir"]]

            if lat_raw is None or lon_raw is None or lat_dir is None or lon_dir is None:
                continue

            lat_val = float(lat_raw)
            lon_val = float(lon_raw)

            lat = lat_val if lat_dir == "N" else -lat_val
            lon = lon_val if lon_dir == "E" else -lon_val

            energy = float(row[idx["energy"]]) if row[idx["energy"]] else 0.0
            impact_e = float(row[idx["impact-e"]]) if row[idx["impact-e"]] else 0.0

            vx = float(row[idx["vx"]]) if "vx" in idx and row[idx["vx"]] else 0.0
            vy = float(row[idx["vy"]]) if "vy" in idx and row[idx["vy"]] else 0.0
            vz = float(row[idx["vz"]]) if "vz" in idx and row[idx["vz"]] else 0.0
            vel = sqrt(vx * vx + vy * vy + vz * vz)

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
