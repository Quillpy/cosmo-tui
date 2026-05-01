from __future__ import annotations

from textual.widgets import DataTable

from ..api.sentry import SentryObject


class SentryWatch(DataTable):
    def __init__(self) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        self.add_columns("Name", "Date Range", "Impact Prob", "Palermo", "Torino", "Size (km)", "Last Obs")

    def set_objects(self, objects: list[SentryObject]) -> None:
        self.clear()
        for obj in objects:
            # Color code by Torino scale
            if obj.torino_scale >= 5:
                name = f"[bold red]{obj.name}[/]"
                torino = f"[bold red]{obj.torino_scale}[/]"
            elif obj.torino_scale >= 1:
                name = f"[yellow]{obj.name}[/]"
                torino = f"[yellow]{obj.torino_scale}[/]"
            else:
                name = obj.name
                torino = f"[green]{obj.torino_scale}[/]"

            # Format Palermo scale with color
            ps = obj.palermo_scale
            if ps > -2:
                ps_str = f"[red]{ps:+.2f}[/]"
            elif ps > -4:
                ps_str = f"[yellow]{ps:+.2f}[/]"
            else:
                ps_str = f"[green]{ps:+.2f}[/]"

            prob = f"{obj.impact_probability:.2e}"
            diam = f"{obj.diameter_km:.3f}" if obj.diameter_km < 1 else f"{obj.diameter_km:.2f}"

            self.add_row(
                name,
                obj.date_range,
                prob,
                ps_str,
                torino,
                diam,
                obj.last_obs,
                key=obj.designation,
            )
