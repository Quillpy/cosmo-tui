from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files

_BRAILLE_BITS = {
    (0, 0): 0x01, (1, 0): 0x02, (2, 0): 0x04, (3, 0): 0x40,
    (0, 1): 0x08, (1, 1): 0x10, (2, 1): 0x20, (3, 1): 0x80,
}
_BRAILLE_BASE = 0x2800

class MapData:
    def __init__(self, grid_size: int = 12):
        self.grid_size = grid_size
        self.polygons = []
        self.spatial_grid = [[[] for _ in range(grid_size)] for _ in range(grid_size)]
        self._load()

    def _load(self) -> None:
        path = files("cosmo.data").joinpath("ne_110m_land.geojson")
        with path.open("r", encoding="utf-8") as f:
            gj = json.load(f)
        
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
                self.polygons.append(((min(xs), min(ys), max(xs), max(ys)), rings))
        
        for i, ((minx, miny, maxx, maxy), _) in enumerate(self.polygons):
            gx_start = max(0, int((minx + 180.0) / 360.0 * self.grid_size))
            gx_end = min(self.grid_size - 1, int((maxx + 180.0) / 360.0 * self.grid_size))
            gy_start = max(0, int((90.0 - maxy) / 180.0 * self.grid_size))
            gy_end = min(self.grid_size - 1, int((90.0 - miny) / 180.0 * self.grid_size))

            for gy in range(gy_start, gy_end + 1):
                for gx in range(gx_start, gx_end + 1):
                    self.spatial_grid[gy][gx].append(i)

    def is_land(self, lat: float, lon: float) -> bool:
        gx = max(0, min(self.grid_size - 1, int((lon + 180.0) / 360.0 * self.grid_size)))
        gy = max(0, min(self.grid_size - 1, int((90.0 - lat) / 180.0 * self.grid_size)))

        for idx in self.spatial_grid[gy][gx]:
            (minx, miny, maxx, maxy), rings = self.polygons[idx]
            if minx <= lon <= maxx and miny <= lat <= maxy:
                if self._point_in_ring(lon, lat, rings[0]):
                    for hole in rings[1:]:
                        if self._point_in_ring(lon, lat, hole):
                            break
                    else:
                        return True
        return False

    @staticmethod
    def _point_in_ring(lon: float, lat: float, ring: list[tuple[float, float]]) -> bool:
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


@lru_cache(maxsize=1)
def get_map_data() -> MapData:
    return MapData()


@lru_cache(maxsize=4)
def build_cells(w_cells: int, h_cells: int) -> tuple[str, ...]:
    """Return one braille string per terminal row, width = w_cells chars."""
    w_px = w_cells * 2
    h_px = h_cells * 4
    md = get_map_data()

    mask: list[list[bool]] = []
    for py in range(h_px):
        lat = 90.0 - (py + 0.5) / h_px * 180.0
        row = [False] * w_px
        for px in range(w_px):
            lon = -180.0 + (px + 0.5) / w_px * 360.0
            row[px] = md.is_land(lat, lon)
        mask.append(row)

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

def project(lat: float, lon: float, w: int, h: int) -> tuple[int, int]:
    col = int((lon + 180.0) / 360.0 * w)
    row = int((90.0 - lat) / 180.0 * h)
    col = max(0, min(w - 1, col))
    row = max(0, min(h - 1, row))
    return col, row
