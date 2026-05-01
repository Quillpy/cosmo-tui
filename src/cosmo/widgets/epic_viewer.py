from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from textual.binding import Binding
from ..api.epic import EpicImage
from ..utils.download import download_image

class EpicViewer(Widget):
    BINDINGS = [
        Binding("s", "save", "Save Latest"),
    ]
    can_focus = True
    images: reactive[list[EpicImage]] = reactive(list, recompose=False)

    def set_images(self, images: list[EpicImage]) -> None:
        self.images = list(images)
        self.refresh()

    async def action_save(self) -> None:
        if not self.images:
            self.app.notify("No images available to save", severity="error")
            return
        
        img = self.images[0]
        try:
            path = await download_image(img.image_url, f"epic_{img.date}")
            self.app.notify(f"Image saved to {path}", title="Success")
        except Exception as e:
            self.app.notify(f"Failed to save image: {e}", severity="error")

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
