from __future__ import annotations

from dataclasses import dataclass

from .client import NasaClient

SENTRY_URL = "https://ssd-api.jpl.nasa.gov/sentry.api"


@dataclass
class SentryObject:
    name: str
    designation: str
    date_range: str
    impact_probability: float
    palermo_scale: float
    torino_scale: int
    diameter_km: float
    n_impacts: int
    last_obs: str


async def fetch_sentry_objects(client: NasaClient) -> list[SentryObject]:
    """Fetch NEOs with non-zero Earth impact probability from Sentry."""
    data = await client.get(SENTRY_URL)
    results: list[SentryObject] = []

    for item in data.get("data", []):
        try:
            # Date range from first to last potential impact
            ip_str = item.get("ip", "0")
            ps_str = item.get("ps_max", "0")
            ts_str = item.get("ts_max", "0")
            diam_str = item.get("diameter", "0")
            n_imp_str = item.get("n_imp", "0")

            results.append(SentryObject(
                name=item.get("fullname", item.get("des", "?")),
                designation=item.get("des", ""),
                date_range=item.get("range", ""),
                impact_probability=float(ip_str),
                palermo_scale=float(ps_str),
                torino_scale=int(float(ts_str)),
                diameter_km=float(diam_str),
                n_impacts=int(n_imp_str),
                last_obs=item.get("last_obs", ""),
            ))
        except (KeyError, ValueError, TypeError):
            continue

    # Sort by Palermo scale descending (higher = more concerning)
    results.sort(key=lambda s: s.palermo_scale, reverse=True)
    return results
