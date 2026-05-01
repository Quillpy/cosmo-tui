from __future__ import annotations
from dataclasses import dataclass
from .client import NasaClient

@dataclass
class Exoplanet:
    name: str
    host_star: str
    method: str
    year: int
    pub_date: str

async def fetch_recent_exoplanets(client: NasaClient, limit: int = 10) -> list[Exoplanet]:
    """Fetch most recently discovered exoplanets from NASA Exoplanet Archive."""
    query = f"select top {limit} pl_name,hostname,discoverymethod,disc_year,disc_pubdate from ps order by disc_pubdate desc"
    data = await client.get(
        "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
        params={"query": query, "format": "json"}
    )
    
    planets: list[Exoplanet] = []
    if not isinstance(data, list):
        return planets
        
    for item in data:
        planets.append(Exoplanet(
            name=item.get("pl_name", "Unknown"),
            host_star=item.get("hostname", "Unknown"),
            method=item.get("discoverymethod", "Unknown"),
            year=int(item.get("disc_year", 0)),
            pub_date=item.get("disc_pubdate", "Unknown")
        ))
    
    return planets
