from __future__ import annotations

import asyncio
from dataclasses import dataclass
from .client import NasaClient

MARS_BASE = "https://api.nasa.gov/mars-photos/api/v1/rovers"

@dataclass
class MarsPhoto:
    id: int
    sol: int
    img_src: str
    earth_date: str
    camera_name: str
    rover_name: str

async def fetch_latest_mars_photos(client: NasaClient, rover: str = "perseverance") -> list[MarsPhoto]:
    url = f"{MARS_BASE}/{rover}/latest_photos"
    data = await client.get(url)
    if not isinstance(data, dict):
        return []
    
    photos = data.get("latest_photos", [])
    results = []
    for p in photos[:15]:
        results.append(MarsPhoto(
            id=p.get("id", 0),
            sol=p.get("sol", 0),
            img_src=p.get("img_src", ""),
            earth_date=p.get("earth_date", ""),
            camera_name=p.get("camera", {}).get("full_name", "Unknown"),
            rover_name=p.get("rover", {}).get("name", rover)
        ))
    return results

async def fetch_all_rovers_latest(client: NasaClient) -> list[MarsPhoto]:
    # Perseverance and Curiosity are the main active ones
    results = await asyncio.gather(
        fetch_latest_mars_photos(client, "perseverance"),
        fetch_latest_mars_photos(client, "curiosity"),
        return_exceptions=True
    )
    combined = []
    for res in results:
        if isinstance(res, list):
            combined.extend(res)
    
    # Sort by earth date descending
    combined.sort(key=lambda x: x.earth_date, reverse=True)
    return combined
