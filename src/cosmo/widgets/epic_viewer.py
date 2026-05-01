from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from ..api.epic import EpicImage

class EpicViewer(Widget):
    images: reactive[list[EpicImage]] = reactive(list, recompose=False)

    def set_images(self, images: list[EpicImage]) -> None:
        self.images = list(images)
        self.refresh()

    def render(self) -> Text:
        t = Text()
        if not self.images:
            t.append("Loading EPIC Earth imagery...\n", style="dim")
            return t
        
        t.append("Latest EPIC Earth Imagery\n", style="bold #00d4ff")
        t.append("Daily imagery from the DSCOVR satellite\n\n", style="dim")

        for img in self.images[:5]:
            t.append(f"{img.date} ", style="bold #c678dd")
            t.append(f"({img.lat:.2f}, {img.lon:.2f})\n", style="#555577")
            t.append(f"{img.caption}\n", style="italic")
            t.append("View: ", style="bold")
            t.append(img.image_url + "\n\n", style="underline #00d4ff")
        
        return t
