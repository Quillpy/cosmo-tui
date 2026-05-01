from __future__ import annotations
from dataclasses import dataclass
from .client import NasaClient

@dataclass
class MediaResult:
    nasa_id: str
    title: str
    description: str
    media_type: str
    thumb_url: str
    full_url: str = ""

async def search_nasa_media(client: NasaClient, query: str) -> list[MediaResult]:
    """Search NASA's Image and Video Library."""
    data = await client.get("https://images-api.nasa.gov/search", params={"q": query})
    results: list[MediaResult] = []
    
    if not isinstance(data, dict):
        return results

    collection = data.get("collection", {})
    items = collection.get("items", [])
    
    for item in items:
        meta_list = item.get("data", [])
        if not meta_list:
            continue
        meta = meta_list[0]
        
        links = item.get("links", [])
        thumb = ""
        for link in links:
            if link.get("rel") == "preview":
                thumb = link.get("href", "")
                break
        
        results.append(MediaResult(
            nasa_id=meta.get("nasa_id", ""),
            title=meta.get("title", "Untitled"),
            description=meta.get("description", ""),
            media_type=meta.get("media_type", "image"),
            thumb_url=thumb
        ))
    
    return results[:20]  # Limit to 20 results for TUI performance
