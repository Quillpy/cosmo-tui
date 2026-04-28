from __future__ import annotations

from dataclasses import dataclass

from .client import NasaClient

APOD_URL = "https://api.nasa.gov/planetary/apod"


@dataclass
class Apod:
    title: str
    date: str
    explanation: str
    url: str
    hdurl: str = ""
    media_type: str = "image"
    copyright: str = ""


async def fetch_apod(client: NasaClient) -> Apod:
    data = await client.get(APOD_URL)
    return Apod(
        title=data.get("title", ""),
        date=data.get("date", ""),
        explanation=data.get("explanation", ""),
        url=data.get("url", ""),
        hdurl=data.get("hdurl", ""),
        media_type=data.get("media_type", "image"),
        copyright=data.get("copyright", ""),
    )
