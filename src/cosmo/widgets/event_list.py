from __future__ import annotations

from textual.message import Message
from textual.widgets import DataTable

from ..api.eonet import Event


class EventList(DataTable):
    class EventSelected(Message):
        def __init__(self, event_id: str) -> None:
            self.event_id = event_id
            super().__init__()

    def __init__(self) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True)
        self._events: list[Event] = []

    def on_mount(self) -> None:
        self.add_columns("Date", "Category", "Title")

    def set_events(self, events: list[Event]) -> None:
        self._events = events
        self.clear()
        if not events:
            self.add_row("No recent events", "", "", key="empty")
            return
        for ev in events:
            date = (ev.date or "")[:10]
            cat = f"[{ev.color}]\u25CF[/] {ev.category_title}"
            self.add_row(date, cat, ev.title, key=ev.id)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key and event.row_key.value:
            self.post_message(self.EventSelected(event.row_key.value))
