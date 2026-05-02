from __future__ import annotations

from textual.widgets import DataTable
from ..api.mars import MarsPhoto

class MarsRoverTable(DataTable):
    def __init__(self) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        self.add_columns("Date", "Rover", "Camera", "Sol", "Image URL")

    def set_photos(self, photos: list[MarsPhoto]) -> None:
        self.clear()
        if not photos:
            self.add_row("Mars rover photos API unavailable", "", "", "", "", key="empty")
            return
        for p in photos:
            self.add_row(
                p.earth_date,
                p.rover_name,
                p.camera_name,
                str(p.sol),
                p.img_src,
                key=str(p.id)
            )
