from __future__ import annotations
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget
from ..api.mars_weather import MarsWeather

class MarsWeatherPanel(Widget):
    weather: reactive[MarsWeather | None] = reactive(None)

    def set_weather(self, weather: MarsWeather) -> None:
        self.weather = weather
        self.refresh()

    def render(self) -> Text:
        t = Text()
        if not self.weather:
            t.append("Loading Mars weather data (Curiosity REMS)...\n", style="dim")
            return t
        
        w = self.weather
        t.append(f"Mars Weather at Gale Crater (Sol {w.sol})\n", style="bold #00d4ff")
        t.append(f"Season: {w.season}\n\n", style="dim")
        
        def row(label: str, value: str, color: str):
            t.append(f"{label:15}", style="bold")
            t.append(f"{value}\n", style=color)

        row("Temp Max:", f"{w.temp_max}\u00b0C", "#e06c75")
        row("Temp Min:", f"{w.temp_min}\u00b0C", "#61afef")
        row("Atmo Temp:", f"{w.atmo_temp}\u00b0C", "#98c379")
        row("Pressure:", f"{w.pressure} Pa", "#e5c07b")
        row("Opacity:", w.opacity, "#c678dd")
        
        t.append("\nData provided by CAB/REMS via MAAS2 API.\n", style="dim italic")
        return t
