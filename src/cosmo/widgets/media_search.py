from __future__ import annotations
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Input, Static

from ..api.media_search import MediaResult, search_nasa_media

class MediaSearch(Vertical):
    def __init__(self) -> None:
        super().__init__()
        self._results_by_key: dict[str, MediaResult] = {}

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search NASA Image Library...", id="search-input")
        self.results_table = DataTable(cursor_type="row", id="results-table")
        yield self.results_table
        self.detail = Static("Press Enter to search.", id="help-text", classes="dim")
        yield self.detail

    def on_mount(self) -> None:
        self.results_table.add_columns("Title", "Type", "ID")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
            
        self.app.notify(f"Searching for '{query}'...")
        try:
            results = await search_nasa_media(self.app.client, query)
            self._results_by_key = {}
            self.results_table.clear()
            for index, r in enumerate(results):
                key = f"{index}:{r.nasa_id or r.title}"
                self._results_by_key[key] = r
                self.results_table.add_row(r.title, r.media_type, r.nasa_id, key=key)
            if not results:
                self.detail.update("No results found.")
                self.app.notify("No results found", severity="warning")
            else:
                self.detail.update(f"{len(results)} result(s). Select a row for details.")
        except Exception as e:
            self.app.notify(f"Search failed: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if not event.row_key:
            return
        result = self._results_by_key.get(event.row_key.value)
        if not result:
            return
        description = result.description.replace("\n", " ").strip()
        if len(description) > 240:
            description = description[:237] + "..."
        self.detail.update(f"{result.title}\n{result.media_type} | {result.nasa_id}\n{description}")
