from __future__ import annotations
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget
from ..api.mars_weather import MarsWeather

class MarsWeatherPanel(Widget):
    weather: reactive[MarsWeather | None] = reactive(None)
    error_message: reactive[str] = reactive("")

    def set_weather(self, weather: MarsWeather) -> None:
        self.error_message = ""
        self.weather = weather
        self.refresh()

    def set_error(self, message: str) -> None:
        self.error_message = message
        self.weather = None
        self.refresh()

    def render(self) -> Text:
        t = Text()
        if self.error_message:
            t.append("Mars Weather at Gale Crater\n", style="bold #00d4ff")
            t.append(f"{self.error_message}\n", style="bold red")
            return t
        if not self.weather:
            t.append("Mars Weather at Gale Crater\n", style="bold #00d4ff")
            t.append("Loading latest Curiosity REMS report...\n", style="bold")
            return t
        
        w = self.weather
        t.append(f"Mars Weather at Gale Crater (Sol {w.sol})\n", style="bold #00d4ff")
        t.append(f"Terrestrial Date: {w.terrestrial_date}\n", style="dim")
        t.append(f"Season: {w.season}\n\n", style="dim")
        
        def row(label: str, value: str, color: str):
            t.append(f"{label:15}", style="bold")
            t.append(f"{value}\n", style=color)

        row("Temp Max:", f"{w.temp_max}\u00b0C", "#e06c75")
        row("Temp Min:", f"{w.temp_min}\u00b0C", "#61afef")
        row("Pressure:", f"{w.pressure} Pa", "#e5c07b")
        row("Opacity:", w.atmo_opacity, "#c678dd")
        
        t.append("\nData provided by NASA MSL/CAB REMS.\n", style="dim italic")
        return t
