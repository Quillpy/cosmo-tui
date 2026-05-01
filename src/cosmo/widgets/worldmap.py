"""Dot-matrix world map using Natural Earth 110m land polygons + braille.

Each terminal cell is a 2x4 sub-pixel braille glyph (U+2800..U+28FF),
giving an 8x density boost. Land sub-pixels render as white dots on a
pure black background; ocean is empty space. Event markers are the only
colored elements on the map.
"""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from ..api.eonet import Event
from ..api.fireball import Fireball


# ---------- geojson + point-in-polygon ----------

_POLYGONS = None
_SPATIAL_GRID = None
_GRID_SIZE = 12


def _load_polygons():
    global _POLYGONS, _SPATIAL_GRID
    if _POLYGONS is not None:
        return _POLYGONS
    path = files("cosmo.data").joinpath("ne_110m_land.geojson")
    with path.open("r", encoding="utf-8") as f:
        gj = json.load(f)
    polys = []
    for feature in gj.get("features", []):
        geom = feature.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates") or []
        raws = coords if gtype == "MultiPolygon" else [coords] if gtype == "Polygon" else []
        for poly in raws:
            rings = [[(float(x), float(y)) for x, y in ring] for ring in poly]
            if not rings:
                continue
            xs = [p[0] for p in rings[0]]
            ys = [p[1] for p in rings[0]]
            polys.append(((min(xs), min(ys), max(xs), max(ys)), rings))
    _POLYGONS = polys

    # Build spatial grid for pruning
    _SPATIAL_GRID = [[[] for _ in range(_GRID_SIZE)] for _ in range(_GRID_SIZE)]
    for i, ((minx, miny, maxx, maxy), _) in enumerate(_POLYGONS):
        gx_start = max(0, int((minx + 180.0) / 360.0 * _GRID_SIZE))
        gx_end = min(_GRID_SIZE - 1, int((maxx + 180.0) / 360.0 * _GRID_SIZE))
        gy_start = max(0, int((90.0 - maxy) / 180.0 * _GRID_SIZE))
        gy_end = min(_GRID_SIZE - 1, int((90.0 - miny) / 180.0 * _GRID_SIZE))

        for gy in range(gy_start, gy_end + 1):
            for gx in range(gx_start, gx_end + 1):
                _SPATIAL_GRID[gy][gx].append(i)

    return polys


def _point_in_ring(lon: float, lat: float, ring) -> bool:
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def _is_land(lat: float, lon: float) -> bool:
    polys = _load_polygons()
    gx = max(0, min(_GRID_SIZE - 1, int((lon + 180.0) / 360.0 * _GRID_SIZE)))
    gy = max(0, min(_GRID_SIZE - 1, int((90.0 - lat) / 180.0 * _GRID_SIZE)))

    for idx in _SPATIAL_GRID[gy][gx]:
        (minx, miny, maxx, maxy), rings = polys[idx]
        if minx <= lon <= maxx and miny <= lat <= maxy:
            if _point_in_ring(lon, lat, rings[0]):
                for hole in rings[1:]:
                    if _point_in_ring(lon, lat, hole):
                        break
                else:
                    return True
    return False


# ---------- braille rasterization ----------

# Braille dot bit positions for sub-pixel at (sub_row, sub_col) within a cell:
#   sub_col 0,1  x  sub_row 0..3
# Standard Unicode braille mapping (1..8):
#   (0,0)->1=0x01 (1,0)->2=0x02 (2,0)->3=0x04 (3,0)->7=0x40
#   (0,1)->4=0x08 (1,1)->5=0x10 (2,1)->6=0x20 (3,1)->8=0x80
_BRAILLE_BITS = {
    (0, 0): 0x01, (1, 0): 0x02, (2, 0): 0x04, (3, 0): 0x40,
    (0, 1): 0x08, (1, 1): 0x10, (2, 1): 0x20, (3, 1): 0x80,
}
_BRAILLE_BASE = 0x2800


@lru_cache(maxsize=4)
def _build_cells(w_cells: int, h_cells: int) -> tuple[str, ...]:
    """Return one braille string per terminal row, width = w_cells chars."""
    w_px = w_cells * 2
    h_px = h_cells * 4

    # Sample land mask at sub-pixel resolution
    mask: list[list[bool]] = []
    for py in range(h_px):
        lat = 90.0 - (py + 0.5) / h_px * 180.0
        row = [False] * w_px
        for px in range(w_px):
            lon = -180.0 + (px + 0.5) / w_px * 360.0
            row[px] = _is_land(lat, lon)
        mask.append(row)

    # Compose braille cells
    out: list[str] = []
    for cy in range(h_cells):
        chars: list[str] = []
        for cx in range(w_cells):
            bits = 0
            for (sr, sc), bit in _BRAILLE_BITS.items():
                if mask[cy * 4 + sr][cx * 2 + sc]:
                    bits |= bit
            chars.append(chr(_BRAILLE_BASE + bits))
        out.append("".join(chars))
    return tuple(out)


def _project(lat: float, lon: float, w: int, h: int) -> tuple[int, int]:
    col = int((lon + 180.0) / 360.0 * w)
    row = int((90.0 - lat) / 180.0 * h)
    col = max(0, min(w - 1, col))
    row = max(0, min(h - 1, row))
    return col, row


# ---------- widget ----------

LAND_STYLE = "#a0a0c0 on #0a0a0f"
SEA_STYLE = "on #0a0a0f"


class WorldMap(Widget):
    DEFAULT_CSS = """
    WorldMap { background: #0a0a0f; color: #a0a0c0; }
    """

    events: reactive[list[Event]] = reactive(list)
    fireballs: reactive[list[Fireball]] = reactive(list)
    iss_position: reactive[tuple[float, float] | None] = reactive(None)
    selected_id: reactive[str | None] = reactive(None)

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
        rows = _build_cells(w, h)

        chars: list[list[str]] = [list(r) for r in rows]
        styles: list[list[str]] = [
            [LAND_STYLE if ch != "\u2800" else SEA_STYLE for ch in r] for r in rows
        ]

        # Overlay markers
        for ev in self.events:
            col, row = _project(ev.lat, ev.lon, w, h)
            marker = "X" if ev.id == self.selected_id else "\u25CF"
            chars[row][col] = marker
            styles[row][col] = f"bold {ev.color} on #0a0a0f"

        for fb in self.fireballs:
            col, row = _project(fb.lat, fb.lon, w, h)
            chars[row][col] = "\u2605"
            styles[row][col] = "bold bright_yellow on #0a0a0f"

        if self.iss_position is not None:
            lat, lon = self.iss_position
            col, row = _project(lat, lon, w, h)
            chars[row][col] = "\u2726"
            styles[row][col] = "bold bright_cyan on #0a0a0f"

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
