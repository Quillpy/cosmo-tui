"""Dot-matrix world map using Natural Earth 110m land polygons + braille.

Each terminal cell is a 2x4 sub-pixel braille glyph (U+2800..U+28FF),
giving an 8x density boost. Land sub-pixels render as white dots on a
pure black background; ocean is empty space. Event markers are the only
colored elements on the map.
"""
from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from ..api.eonet import Event
from ..api.fireball import Fireball
from .map_renderer import build_cells, project


class WorldMap(Widget):
    DEFAULT_CSS = """
    WorldMap { background: #0a0a0f; color: #a0a0c0; }
    """

    events: reactive[list[Event]] = reactive(list)
    fireballs: reactive[list[Fireball]] = reactive(list)
    iss_position: reactive[tuple[float, float] | None] = reactive(None)
    selected_id: reactive[str | None] = reactive(None)
    theme_name: reactive[str] = reactive("default")

    def set_events(self, events: list[Event]) -> None:
        self.events = list(events)

    def set_fireballs(self, fireballs: list[Fireball]) -> None:
        self.fireballs = list(fireballs)

    def set_iss(self, lat: float | None, lon: float | None) -> None:
        self.iss_position = (lat, lon) if lat is not None and lon is not None else None

    def set_selected(self, event_id: str | None) -> None:
        self.selected_id = event_id

    def render(self) -> Text:
        w = max(40, self.size.width)
        h = max(10, self.size.height)
        rows = build_cells(w, h)

        chars: list[list[str]] = [list(r) for r in rows]
        
        is_classic = self.theme_name == "classic"
        land_style = "#00ff00 on #000000" if is_classic else "#a0a0c0 on #0a0a0f"
        sea_style = "on #000000" if is_classic else "on #0a0a0f"

        styles: list[list[any]] = [
            [land_style if ch != "\u2800" else sea_style for ch in r] for r in rows
        ]

        # Overlay markers
        for ev in self.events:
            col, row = project(ev.lat, ev.lon, w, h)
            marker = "X" if ev.id == self.selected_id else "\u25CF"
            chars[row][col] = marker
            color = "#00ff00" if is_classic else ev.color
            styles[row][col] = f"bold {color} on #0a0a0f" if not is_classic else "bold #00ff00 on #000000"

        for fb in self.fireballs:
            col, row = project(fb.lat, fb.lon, w, h)
            chars[row][col] = "\u2605"
            color = "#00ff00" if is_classic else "bright_yellow"
            styles[row][col] = f"bold {color} on #0a0a0f" if not is_classic else "bold #00ff00 on #000000"

        if self.iss_position is not None:
            lat, lon = self.iss_position
            col, row = project(lat, lon, w, h)
            chars[row][col] = "\u2726"
            color = "#00ff00" if is_classic else "bright_cyan"
            styles[row][col] = f"bold {color} on #0a0a0f" if not is_classic else "bold #00ff00 on #000000"

        text = Text()
        for r in range(h):
            if not chars[r]:
                continue
            
            curr_style = styles[r][0]
            curr_chunk = [chars[r][0]]
            
            for c in range(1, w):
                st = styles[r][c]
                ch = chars[r][c]
                if st == curr_style:
                    curr_chunk.append(ch)
                else:
                    text.append("".join(curr_chunk), style=curr_style)
                    curr_style = st
                    curr_chunk = [ch]
            
            text.append("".join(curr_chunk), style=curr_style)
            if r < h - 1:
                text.append("\n")
        
        return text
