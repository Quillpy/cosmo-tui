from __future__ import annotations

from datetime import datetime, timezone

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        height: 2;
        background: #0d0d1a;
        color: #a0a0c0;
    }
    """

    last_refresh: reactive[datetime | None] = reactive(None)
    rate_remaining: reactive[int | None] = reactive(None)
    next_refresh_in: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        # We don't need a separate interval because 'next_refresh_in' 
        # is updated every second by the app, which triggers a refresh.
        pass

    def render(self) -> Text:
        now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        now_local = datetime.now().strftime("%H:%M:%S")
        last = self.last_refresh.strftime("%H:%M:%S") if self.last_refresh else "--:--:--"
        rate = f"quota:{self.rate_remaining}" if self.rate_remaining is not None else "quota:?"
        next_in = f"next:{max(0, self.next_refresh_in)}s"
        keys = "[q]uit [r]efresh [tab]panel [?]help"

        t = Text()
        t.append(f" \u2736 cosmo ", style="bold #c678dd")
        t.append(f" {now_local} / {now_utc} ", style="#00d4ff")
        t.append(f" last:{last} ", style="#50c878")
        t.append(f" {next_in} ", style="#e5c07b")
        t.append(f" {rate} ", style="#61afef")
        t.append(f"  {keys}", style="#555577")
        t.append("\n")
        # Map legend
        t.append(" MAP: ", style="bold #555577")
        t.append("\u25CF", style="bold red")
        t.append(" Fire ", style="#555577")
        t.append("\u25CF", style="bold blue")
        t.append(" Storm ", style="#555577")
        t.append("\u25CF", style="bold yellow")
        t.append(" Quake ", style="#555577")
        t.append("\u25CF", style="bold orange3")
        t.append(" Volcano ", style="#555577")
        t.append("\u25CF", style="bold green")
        t.append(" Flood ", style="#555577")
        t.append("\u2605", style="bold bright_yellow")
        t.append(" Fireball ", style="#555577")
        t.append("\u2726", style="bold bright_cyan")
        t.append(" ISS", style="#555577")
        return t
