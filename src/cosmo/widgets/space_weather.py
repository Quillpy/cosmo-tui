from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from ..api.donki import WeatherEvent


KIND_COLORS = {
    "FLR": "#e5c07b",
    "CME": "#c678dd",
    "GST": "#e06c75",
    "SEP": "#00d4ff",
}


class SpaceWeatherPanel(Widget):
    events: reactive[list[WeatherEvent]] = reactive(list, recompose=False)

    def set_events(self, events: list[WeatherEvent]) -> None:
        self.events = list(events)
        self.refresh()

    def _summary(self) -> tuple[str, str]:
        if not self.events:
            return "Quiet", "green"
        kps = [e for e in self.events if e.kind == "GST"]
        flares = [e for e in self.events if e.kind == "FLR"]
        level = "Minor"
        color = "yellow"
        for f in flares:
            cls = f.severity or ""
            if cls.startswith("X"):
                level, color = "Severe", "bright_red"
                break
            if cls.startswith("M"):
                level, color = "Strong", "red"
        if kps:
            level = level if level != "Minor" else "Moderate"
        return level, color

    def render(self) -> Text:
        t = Text()
        level, color = self._summary()
        t.append("Space Weather Status: ", style="bold")
        t.append(level + "\n\n", style=f"bold {color}")

        if not self.events:
            t.append("No recent space weather events.\n", style="dim")
            return t

        for e in self.events[:12]:
            when = (e.time or "")[:16].replace("T", " ")
            t.append(f"{when}  ", style="dim")
            t.append(f"{e.kind}", style=f"bold {KIND_COLORS.get(e.kind, 'white')}")
            if e.severity:
                t.append(f" [{e.severity}]", style="yellow")
            t.append(f"  {e.summary}\n")
        return t
