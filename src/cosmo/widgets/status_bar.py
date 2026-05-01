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
    theme_name: reactive[str] = reactive("default")

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

        is_classic = self.theme_name == "classic"
        
        t = Text()
        t.append(f" \u2736 cosmo ", style="bold #c678dd" if not is_classic else "bold #00ff00")
        t.append(f" {now_local} / {now_utc} ", style="#00d4ff" if not is_classic else "#00ff00")
        t.append(f" last:{last} ", style="#50c878" if not is_classic else "#00ff00")
        t.append(f" {next_in} ", style="#e5c07b" if not is_classic else "#00ff00")
        t.append(f" {rate} ", style="#61afef" if not is_classic else "#00ff00")
        t.append(f"  {keys}", style="#555577" if not is_classic else "#00ff00")
        t.append("\n")
        # Map legend
        t.append(" MAP: ", style="bold #555577" if not is_classic else "bold #00ff00")
        
        def sym(s, color):
            t.append(s, style=f"bold {color}" if not is_classic else "bold #00ff00")

        sym("\u25CF", "red")
        t.append(" Fire ", style="#555577" if not is_classic else "#00ff00")
        sym("\u25CF", "blue")
        t.append(" Storm ", style="#555577" if not is_classic else "#00ff00")
        sym("\u25CF", "yellow")
        t.append(" Quake ", style="#555577" if not is_classic else "#00ff00")
        sym("\u25CF", "orange3")
        t.append(" Volcano ", style="#555577" if not is_classic else "#00ff00")
        sym("\u25CF", "green")
        t.append(" Flood ", style="#555577" if not is_classic else "#00ff00")
        sym("\u2605", "bright_yellow")
        t.append(" Fireball ", style="#555577" if not is_classic else "#00ff00")
        sym("\u2726", "bright_cyan")
        t.append(" ISS", style="#555577" if not is_classic else "#00ff00")
        return t
