from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from textual.binding import Binding
from ..api.apod import Apod
from ..utils.download import download_image

class ApodViewer(Widget):
    BINDINGS = [
        Binding("s", "save", "Save Image"),
    ]
    can_focus = True
    apod: reactive[Apod | None] = reactive(None, recompose=False)

    def set_apod(self, apod: Apod | None) -> None:
        self.apod = apod
        self.refresh()

    async def action_save(self) -> None:
        if not self.apod or not self.apod.url:
            self.app.notify("No image available to save", severity="error")
            return
        
        url = self.apod.hdurl or self.apod.url
        try:
            path = await download_image(url, f"apod_{self.apod.date}")
            self.app.notify(f"Image saved to {path}", title="Success")
        except Exception as e:
            self.app.notify(f"Failed to save image: {e}", severity="error")

    def render(self) -> Text:
        t = Text()
        if not self.apod:
            t.append("Loading Astronomy Picture of the Day...\n", style="dim")
            return t
        a = self.apod
        t.append(f"{a.title}\n", style="bold #c678dd")
        t.append(f"{a.date}", style="#555577")
        if a.copyright:
            t.append(f"  \u00A9 {a.copyright}", style="#555577")
        t.append("\n\n")
        explanation = a.explanation
        if len(explanation) > 600:
            explanation = explanation[:597] + "..."
        t.append(explanation + "\n\n")
        if a.url:
            t.append("View: ", style="bold #a0a0c0")
            t.append(a.hdurl or a.url, style="underline #00d4ff")
            t.append("\n")
        if a.media_type != "image":
            t.append(f"\n[media: {a.media_type}]\n", style="#e5c07b")
        return t
