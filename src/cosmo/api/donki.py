from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .client import NasaClient

DONKI_BASE = "https://api.nasa.gov/DONKI"


@dataclass
class WeatherEvent:
    kind: str
    time: str
    summary: str
    severity: str = ""


def _date_range(days: int = 7) -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


async def fetch_space_weather(client: NasaClient, days: int = 7) -> list[WeatherEvent]:
    start, end = _date_range(days)
    events: list[WeatherEvent] = []

    async def safe(url: str, params: dict) -> list:
        try:
            data = await client.get(url, params=params)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    params = {"startDate": start, "endDate": end}

    for item in await safe(f"{DONKI_BASE}/FLR", params):
        events.append(WeatherEvent(
            kind="FLR",
            time=item.get("beginTime", ""),
            summary=f"Solar flare class {item.get('classType', '?')} from {item.get('sourceLocation', '?')}",
            severity=item.get("classType", ""),
        ))
    for item in await safe(f"{DONKI_BASE}/CME", params):
        events.append(WeatherEvent(
            kind="CME",
            time=item.get("startTime", ""),
            summary=item.get("note", "Coronal Mass Ejection")[:80],
        ))
    for item in await safe(f"{DONKI_BASE}/GST", params):
        kp = item.get("allKpIndex") or []
        max_kp = max((k.get("kpIndex", 0) for k in kp), default=0)
        events.append(WeatherEvent(
            kind="GST",
            time=item.get("startTime", ""),
            summary=f"Geomagnetic storm, max Kp={max_kp}",
            severity=f"Kp{max_kp}",
        ))
    for item in await safe(f"{DONKI_BASE}/SEP", params):
        events.append(WeatherEvent(
            kind="SEP",
            time=item.get("eventTime", ""),
            summary="Solar Energetic Particle event",
        ))

    events.sort(key=lambda e: e.time, reverse=True)
    return events
