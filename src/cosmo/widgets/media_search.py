from __future__ import annotations
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import Input, Static, DataTable, ListItem, ListView
from textual.containers import Vertical, Horizontal
from ..api.media_search import search_nasa_media, MediaResult

class MediaSearch(Vertical):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search NASA Image Library...", id="search-input")
        self.results_table = DataTable(cursor_type="row", id="results-table")
        yield self.results_table
        yield Static("Press Enter to search. Row to see details.", id="help-text", classes="dim")

    def on_mount(self) -> None:
        self.results_table.add_columns("Title", "Type", "ID")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
            
        self.app.notify(f"Searching for '{query}'...")
        try:
            results = await search_nasa_media(self.app.client, query)
            self.results_table.clear()
            for r in results:
                self.results_table.add_row(r.title, r.media_type, r.nasa_id, key=r.nasa_id)
            if not results:
                self.app.notify("No results found", severity="warning")
        except Exception as e:
            self.app.notify(f"Search failed: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # In a real app we'd show a detail view, but for now we'll just notify
        self.app.notify(f"Selected: {event.row_key.value}")
