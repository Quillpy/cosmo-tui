from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sgp4.api import Satrec, jday

from .client import NasaClient

TLE_URLS = [
    "https://tle.ivanstanojevic.me/api/tle/25544",  # primary
    "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE",  # fallback
]


@dataclass
class ISSPosition:
    lat: float
    lon: float
    altitude_km: float
    velocity_kms: float
    timestamp: datetime


def _propagate(line1: str, line2: str) -> ISSPosition:
    """Compute current ISS position from TLE lines using SGP4."""
    sat = Satrec.twoline2rv(line1, line2)
    now = datetime.now(timezone.utc)
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute,
                  now.second + now.microsecond / 1e6)
    e, r, v = sat.sgp4(jd, fr)
    if e != 0:
        raise RuntimeError(f"SGP4 propagation error code {e}")

    # r is position in km (TEME frame), v is velocity in km/s
    x, y, z = r
    vx, vy, vz = v

    # Convert TEME to lat/lon (simplified: ignoring Earth rotation precisely,
    # using Greenwich Mean Sidereal Time for longitude correction)
    from math import atan2, sqrt, degrees, pi

    # Earth radius
    r_mag = sqrt(x * x + y * y + z * z)
    lat = degrees(atan2(z, sqrt(x * x + y * y)))

    # GMST for longitude correction
    # Julian centuries from J2000.0
    jd_total = jd + fr
    t_ut1 = (jd_total - 2451545.0) / 36525.0
    gmst = (67310.54841
            + (876600.0 * 3600.0 + 8640184.812866) * t_ut1
            + 0.093104 * t_ut1 ** 2
            - 6.2e-6 * t_ut1 ** 3)
    gmst_deg = (gmst % 86400.0) / 240.0  # convert seconds to degrees

    lon = degrees(atan2(y, x)) - gmst_deg
    # Normalize longitude to [-180, 180]
    lon = ((lon + 180.0) % 360.0) - 180.0

    altitude = r_mag - 6371.0  # approximate Earth radius
    speed = sqrt(vx * vx + vy * vy + vz * vz)

    return ISSPosition(
        lat=lat, lon=lon, altitude_km=altitude, velocity_kms=speed,
        timestamp=now,
    )


# Cache the TLE lines so we don't re-fetch every 30s
_cached_tle: tuple[str, str] | None = None
_cached_at: datetime | None = None
_CACHE_TTL_SECONDS = 3600  # re-fetch TLE once per hour


async def _fetch_tle_from_json(client: NasaClient, url: str) -> tuple[str, str]:
    """Fetch TLE from a JSON API (tle.ivanstanojevic.me style)."""
    data = await client.get(url)
    line1 = data.get("line1", "")
    line2 = data.get("line2", "")
    if not line1 or not line2:
        raise ValueError("Empty TLE data")
    return line1, line2


async def _fetch_tle_from_text(client: NasaClient, url: str) -> tuple[str, str]:
    """Fetch TLE from a plain-text 3LE source (CelesTrak style)."""
    import httpx
    r = await client._client.get(url)
    r.raise_for_status()
    lines = [l.strip() for l in r.text.strip().splitlines() if l.strip()]
    # 3LE format: name, line1, line2
    for i, line in enumerate(lines):
        if line.startswith("1 ") and i + 1 < len(lines) and lines[i + 1].startswith("2 "):
            return line, lines[i + 1]
    raise ValueError("Could not parse TLE lines from text response")


async def fetch_iss_position(client: NasaClient) -> ISSPosition:
    """Fetch TLE (cached for 1h) and compute current ISS lat/lon."""
    global _cached_tle, _cached_at

    now = datetime.now(timezone.utc)
    if (_cached_tle is None
            or _cached_at is None
            or (now - _cached_at).total_seconds() > _CACHE_TTL_SECONDS):
        last_err = None
        for url in TLE_URLS:
            try:
                if "celestrak" in url:
                    _cached_tle = await _fetch_tle_from_text(client, url)
                else:
                    _cached_tle = await _fetch_tle_from_json(client, url)
                _cached_at = now
                break
            except Exception as e:
                last_err = e
                continue
        else:
            raise RuntimeError(f"All TLE sources failed: {last_err}")

    return _propagate(_cached_tle[0], _cached_tle[1])
