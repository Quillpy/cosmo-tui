from __future__ import annotations
from textual.widgets import DataTable
from ..api.exoplanet import Exoplanet

class ExoplanetTable(DataTable):
    def __init__(self) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        self.add_columns("Planet Name", "Host Star", "Method", "Year", "Published")

    def set_planets(self, planets: list[Exoplanet]) -> None:
        self.clear()
        if not planets:
            self.add_row("No exoplanets returned", "", "", "", "", key="empty")
            return
        for p in planets:
            self.add_row(
                p.name,
                p.host_star,
                p.method,
                str(p.year),
                p.pub_date,
                key=p.name
            )
