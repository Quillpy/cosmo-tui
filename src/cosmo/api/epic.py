from __future__ import annotations

from dataclasses import dataclass
from .client import NasaClient

EPIC_BASE = "https://api.nasa.gov/EPIC/api/natural"

@dataclass
class EpicImage:
    identifier: str
    caption: str
    image_name: str
    date: str
    lat: float
    lon: float

    @property
    def image_url(self) -> str:
        # Example: https://epic.gsfc.nasa.gov/archive/natural/2015/10/31/png/epic_1b_20151031075642.png
        # Date format in response: "2023-05-01 00:10:44"
        d = self.date.split(" ")[0].replace("-", "/")
        return f"https://epic.gsfc.nasa.gov/archive/natural/{d}/png/{self.image_name}.png"

async def fetch_latest_epic(client: NasaClient) -> list[EpicImage]:
    data = await client.get(EPIC_BASE)
    if not isinstance(data, list):
        return []
    
    results = []
    for item in data[:10]:
        try:
            coords = item.get("centroid_coordinates", {})
            results.append(EpicImage(
                identifier=item.get("identifier", ""),
                caption=item.get("caption", ""),
                image_name=item.get("image", ""),
                date=item.get("date", ""),
                lat=float(coords.get("lat", 0)),
                lon=float(coords.get("lon", 0))
            ))
        except (ValueError, TypeError):
            continue
    return results
