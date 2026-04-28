from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .client import NasaClient

EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"

CATEGORY_COLORS = {
    "wildfires": "red",
    "severeStorms": "blue",
    "earthquakes": "yellow",
    "volcanoes": "orange3",
    "floods": "green",
    "seaLakeIce": "cyan",
    "drought": "rgb(180,140,80)",
    "dustHaze": "rgb(200,180,140)",
    "landslides": "magenta",
    "manmade": "white",
    "snow": "bright_white",
    "tempExtremes": "bright_red",
    "waterColor": "bright_blue",
}


@dataclass
class Event:
    id: str
    title: str
    category_id: str
    category_title: str
    date: str
    lat: float
    lon: float
    source_url: str = ""

    @property
    def color(self) -> str:
        return CATEGORY_COLORS.get(self.category_id, "white")


async def fetch_events(client: NasaClient, limit: int = 100, days: int = 30) -> list[Event]:
    data = await client.get(EONET_URL, params={"limit": limit, "days": days, "status": "open"})
    events: list[Event] = []
    for item in data.get("events", []):
        cats = item.get("categories") or []
        if not cats:
            continue
        cat = cats[0]
        geoms = item.get("geometry") or []
        if not geoms:
            continue
        last = geoms[-1]
        coords = last.get("coordinates")
        if not coords or len(coords) < 2:
            continue
        lon, lat = coords[0], coords[1]
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            continue
        sources = item.get("sources") or []
        src_url = sources[0]["url"] if sources and "url" in sources[0] else ""
        events.append(
            Event(
                id=item.get("id", ""),
                title=item.get("title", "Unknown"),
                category_id=cat.get("id", ""),
                category_title=cat.get("title", ""),
                date=last.get("date", ""),
                lat=lat,
                lon=lon,
                source_url=src_url,
            )
        )
    return events
