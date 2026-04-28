from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from ..api.apod import Apod


class ApodViewer(Widget):
    apod: reactive[Apod | None] = reactive(None, recompose=False)

    def set_apod(self, apod: Apod | None) -> None:
        self.apod = apod
        self.refresh()

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
