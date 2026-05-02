from __future__ import annotations

from textual.widgets import DataTable

from ..api.neows import Neo


class AsteroidTable(DataTable):
    def __init__(self) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        self.add_columns("Date", "Name", "Size (m)", "Miss (LD)", "V (km/s)", "!")

    def set_neos(self, neos: list[Neo]) -> None:
        self.clear()
        if not neos:
            self.add_row("No near-Earth objects available", "", "", "", "", "", key="empty")
            return
        for n in neos:
            date = (n.date or "")[:16]
            size = f"{n.diameter_min_m:.0f}-{n.diameter_max_m:.0f}"
            miss = f"{n.miss_lunar:.2f}"
            vel = f"{n.velocity_kms:.1f}"
            flag = "[red]\u26A0[/]" if n.hazardous else "[green]\u2713[/]"
            name = f"[red]{n.name}[/]" if n.hazardous else n.name
            # Use name as a key since Neo doesn't have a better unique ID
            self.add_row(date, name, size, miss, vel, flag, key=n.name)
