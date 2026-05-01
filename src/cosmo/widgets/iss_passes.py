from __future__ import annotations
from datetime import datetime
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget
from ..api.client import NasaClient
from ..api.geolocation import fetch_user_location

class IssPasses(Widget):
    location_info: reactive[str] = reactive("Detecting location...")
    passes: reactive[list[dict]] = reactive(list)

    async def refresh_passes(self, client: NasaClient) -> None:
        try:
            loc = await fetch_user_location(client)
            self.location_info = f"Location: {loc.city}, {loc.country} ({loc.lat:.2f}, {loc.lon:.2f})"
            
            # Fetch passes from open-notify
            params = {"lat": loc.lat, "lon": loc.lon, "n": 5}
            data = await client.get("http://api.open-notify.org/iss-pass.json", params=params)
            
            if isinstance(data, dict) and data.get("message") == "success":
                self.passes = data.get("response", [])
            else:
                self.passes = []
        except Exception as e:
            self.location_info = f"Location detection failed: {e}"
            self.passes = []

    def render(self) -> Text:
        t = Text()
        t.append("ISS Pass Predictions\n", style="bold #00d4ff")
        t.append(f"{self.location_info}\n\n", style="dim")
        
        if not self.passes:
            t.append("No upcoming passes found or service unavailable.\n", style="dim")
            return t
            
        t.append(f"{'Date & Time':25} {'Duration':10}\n", style="bold underline")
        for p in self.passes:
            dt = datetime.fromtimestamp(p['risetime']).strftime('%Y-%m-%d %H:%M:%S')
            dur = f"{p['duration'] // 60}m {p['duration'] % 60}s"
            t.append(f"{dt:25} {dur:10}\n")
            
        return t
