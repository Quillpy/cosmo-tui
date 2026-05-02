from __future__ import annotations

import asyncio
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

    params = {"startDate": start, "endDate": end}

    async def safe_fetch(path: str) -> list[dict]:
        try:
            data = await client.get(f"{DONKI_BASE}/{path}", params)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    results = await asyncio.gather(
        safe_fetch("FLR"),
        safe_fetch("CME"),
        safe_fetch("GST"),
        safe_fetch("SEP"),
    )

    flr_data, cme_data, gst_data, sep_data = results

    for item in flr_data:
        events.append(WeatherEvent(
            kind="FLR",
            time=item.get("beginTime") or "",
            summary=f"Solar flare class {item.get('classType') or '?'} from {item.get('sourceLocation') or '?'}",
            severity=item.get("classType") or "",
        ))
    for item in cme_data:
        events.append(WeatherEvent(
            kind="CME",
            time=item.get("startTime") or "",
            summary=(item.get("note") or "Coronal Mass Ejection")[:80],
        ))
    for item in gst_data:
        kp = item.get("allKpIndex") or []
        max_kp = max((k.get("kpIndex", 0) for k in kp), default=0)
        events.append(WeatherEvent(
            kind="GST",
            time=item.get("startTime") or "",
            summary=f"Geomagnetic storm, max Kp={max_kp}",
            severity=f"Kp{max_kp}",
        ))
    for item in sep_data:
        events.append(WeatherEvent(
            kind="SEP",
            time=item.get("eventTime") or "",
            summary="Solar Energetic Particle event",
        ))

    events.sort(key=lambda e: e.time, reverse=True)
    return events
