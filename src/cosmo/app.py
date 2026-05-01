from __future__ import annotations

import asyncio
from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, TabbedContent, TabPane

from .api.apod import fetch_apod
from .api.client import NasaClient
from .api.donki import fetch_space_weather
from .api.eonet import fetch_events
from .api.epic import fetch_latest_epic
from .api.fireball import fetch_fireballs
from .api.mars import fetch_all_rovers_latest
from .api.neows import fetch_neos
from .api.sentry import fetch_sentry_objects
from .api.tle import fetch_iss_position
from .config import Config
from .widgets.apod_viewer import ApodViewer
from .widgets.asteroid import AsteroidTable
from .widgets.epic_viewer import EpicViewer
from .widgets.event_list import EventList
from .widgets.mars_rover import MarsRoverTable
from .widgets.sentry_watch import SentryWatch
from .widgets.space_weather import SpaceWeatherPanel
from .widgets.status_bar import StatusBar
from .widgets.worldmap import WorldMap


class CosmoApp(App):
    CSS = """
    $bg-base: #0a0a0f;
    $bg-panel: #0d0d1a;
    $bg-active: #1a1a2e;
    $bg-cursor: #1a1a3e;
    $bg-row-even: #0c0c14;
    
    $fg-base: #a0a0c0;
    $fg-muted: #555577;
    $fg-accent: #00d4ff;
    $fg-highlight: #c678dd;
    $fg-cursor: #e0e0ff;

    $border-normal: #1a3a4a;
    $border-event: #2a1a3a;

    Screen {
        layout: vertical;
        background: $bg-base;
    }

    Screen.theme-classic {
        background: #000000;
    }

    Screen.theme-classic #map-pane {
        border: solid #00ff00;
        border-title-color: #00ff00;
    }

    Screen.theme-classic EventList {
        border: solid #00ff00;
        border-title-color: #00ff00;
    }

    Screen.theme-classic TabbedContent {
        border: solid #00ff00;
    }

    Screen.theme-classic Header {
        background: #000000;
        color: #00ff00;
    }

    Screen.theme-classic Footer {
        background: #000000;
        color: #00ff00;
    }

    Screen.theme-classic Footer > .footer--key {
        background: #001100;
        color: #00ff00;
    }

    Screen.theme-classic Footer > .footer--description {
        color: #00ff00;
    }

    Screen.theme-classic DataTable {
        background: #000000;
        color: #00ff00;
    }

    Screen.theme-classic DataTable > .datatable--header {
        background: #000000;
        color: #00ff00;
    }

    Screen.theme-classic DataTable > .datatable--cursor {
        background: #003300;
        color: #00ff00;
    }

    Screen.theme-classic DataTable > .datatable--even-row {
        background: #050505;
    }

    Screen.theme-classic TabbedContent ContentSwitcher {
        background: #000000;
    }

    Screen.theme-classic Tabs {
        background: #000000;
    }

    Screen.theme-classic Tab {
        color: #00ff00;
        background: #000000;
    }

    Screen.theme-classic Tab.-active {
        color: #00ff00;
        background: #001100;
    }

    Screen.theme-classic TabPane {
        background: #000000;
    }

    #main { height: 1fr; }
    #map-pane {
        width: 2fr;
        border: solid $border-normal;
        border-title-color: $fg-accent;
    }
    #side-pane { width: 1fr; }
    WorldMap { height: 1fr; }
    EventList {
        height: 1fr;
        border: solid $border-event;
        border-title-color: $fg-highlight;
    }
    TabbedContent {
        height: 1fr;
        border: solid $border-normal;
    }
    SpaceWeatherPanel, ApodViewer { padding: 1; }
    StatusBar { height: 2; }

    Header {
        background: $bg-panel;
        color: $fg-accent;
    }
    Footer {
        background: $bg-panel;
        color: $fg-muted;
    }
    Footer > .footer--key {
        background: $bg-active;
        color: $fg-accent;
    }
    Footer > .footer--description {
        color: $fg-muted;
    }

    DataTable {
        background: $bg-base;
        color: $fg-base;
    }
    DataTable > .datatable--header {
        background: $bg-panel;
        color: $fg-accent;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: $bg-cursor;
        color: $fg-cursor;
    }
    DataTable > .datatable--even-row {
        background: $bg-row-even;
    }
    DataTable > .datatable--odd-row {
        background: $bg-base;
    }

    TabbedContent ContentSwitcher {
        background: $bg-base;
    }
    Tabs {
        background: $bg-panel;
    }
    Tab {
        color: $fg-muted;
        background: $bg-panel;
    }
    Tab.-active {
        color: $fg-accent;
        background: $bg-active;
        text-style: bold;
    }
    Tab:hover {
        color: $fg-highlight;
    }
    TabPane {
        background: $bg-base;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("question_mark", "help", "Help"),
        Binding("1", "focus_panel('map')", "Map"),
        Binding("2", "focus_panel('events')", "Events"),
        Binding("3", "focus_panel('tabs')", "Tabs"),
    ]

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.client = NasaClient(api_key=config.api_key)
        self.world_map: WorldMap | None = None
        self.event_list: EventList | None = None
        self.asteroid_table: AsteroidTable | None = None
        self.weather_panel: SpaceWeatherPanel | None = None
        self.apod_viewer: ApodViewer | None = None
        self.sentry_watch: SentryWatch | None = None
        self.epic_viewer: EpicViewer | None = None
        self.mars_table: MarsRoverTable | None = None
        self.status_bar: StatusBar | None = None
        self._refreshing = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            with Container(id="map-pane"):
                self.world_map = WorldMap()
                self.world_map.theme_name = self.config.theme
                yield self.world_map
            with Vertical(id="side-pane"):
                self.event_list = EventList()
                yield self.event_list
                with TabbedContent():
                    with TabPane("Asteroids", id="tab-neo"):
                        self.asteroid_table = AsteroidTable()
                        yield self.asteroid_table
                    with TabPane("Space Weather", id="tab-weather"):
                        self.weather_panel = SpaceWeatherPanel()
                        yield self.weather_panel
                    with TabPane("APOD", id="tab-apod"):
                        self.apod_viewer = ApodViewer()
                        yield self.apod_viewer
                    with TabPane("Mars", id="tab-mars"):
                        self.mars_table = MarsRoverTable()
                        yield self.mars_table
                    with TabPane("EPIC", id="tab-epic"):
                        self.epic_viewer = EpicViewer()
                        yield self.epic_viewer
                    with TabPane("Sentry Watch", id="tab-sentry"):
                        self.sentry_watch = SentryWatch()
                        yield self.sentry_watch
        self.status_bar = StatusBar()
        self.status_bar.theme_name = self.config.theme
        yield self.status_bar
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "cosmo"
        self.sub_title = "NASA Terminal Dashboard"
        self.screen.add_class(f"theme-{self.config.theme}")
        
        await self.refresh_all()
        interval = max(30, self.config.refresh_interval_seconds)
        self.set_interval(interval, lambda: asyncio.create_task(self.refresh_all()))
        self.set_interval(1.0, self._tick)
        # ISS position updates every 30 seconds (local SGP4 computation)
        self.set_interval(30, lambda: asyncio.create_task(self._update_iss()))

    def _tick(self) -> None:
        if self.status_bar and self.status_bar.next_refresh_in > 0:
            self.status_bar.next_refresh_in -= 1

    async def on_unmount(self) -> None:
        await self.client.close()

    async def refresh_all(self) -> None:
        if self._refreshing:
            return
        self._refreshing = True
        
        if self.status_bar:
            self.status_bar.next_refresh_in = max(30, self.config.refresh_interval_seconds)
        
        try:
            await asyncio.gather(
                self._load_events(),
                self._load_neos(),
                self._load_weather(),
                self._load_apod(),
                self._load_fireballs(),
                self._load_sentry(),
                self._load_mars(),
                self._load_epic(),
                self._update_iss(),
                return_exceptions=True,
            )
            if self.status_bar:
                self.status_bar.last_refresh = datetime.now()
                self.status_bar.rate_remaining = self.client.rate_limit_remaining
        finally:
            self._refreshing = False

    async def _load_events(self) -> None:
        try:
            events = await fetch_events(self.client, limit=80, days=30)
            if self.world_map:
                self.world_map.set_events(events)
            if self.event_list:
                self.event_list.set_events(events)
        except Exception as e:
            self.notify(f"Failed to load events: {e}", title="API Error", severity="error")

    async def _load_neos(self) -> None:
        try:
            neos = await fetch_neos(self.client, days=7)
            if self.asteroid_table:
                self.asteroid_table.set_neos(neos)
        except Exception as e:
            self.notify(f"Failed to load neos: {e}", title="API Error", severity="error")

    async def _load_weather(self) -> None:
        try:
            evs = await fetch_space_weather(self.client, days=7)
            if self.weather_panel:
                self.weather_panel.set_events(evs)
        except Exception as e:
            self.notify(f"Failed to load weather: {e}", title="API Error", severity="error")

    async def _load_apod(self) -> None:
        try:
            apod = await fetch_apod(self.client)
            if self.apod_viewer:
                self.apod_viewer.set_apod(apod)
        except Exception as e:
            self.notify(f"Failed to load apod: {e}", title="API Error", severity="error")

    async def _load_fireballs(self) -> None:
        try:
            fireballs = await fetch_fireballs(self.client, days=365)
            if self.world_map:
                self.world_map.set_fireballs(fireballs)
        except Exception as e:
            self.notify(f"Failed to load fireballs: {e}", title="API Error", severity="error")

    async def _load_sentry(self) -> None:
        try:
            objects = await fetch_sentry_objects(self.client)
            if self.sentry_watch:
                self.sentry_watch.set_objects(objects)
        except Exception as e:
            self.notify(f"Failed to load sentry objects: {e}", title="API Error", severity="error")

    async def _load_mars(self) -> None:
        try:
            photos = await fetch_all_rovers_latest(self.client)
            if self.mars_table:
                self.mars_table.set_photos(photos)
        except Exception as e:
            self.notify(f"Failed to load mars photos: {e}", title="API Error", severity="error")

    async def _load_epic(self) -> None:
        try:
            images = await fetch_latest_epic(self.client)
            if self.epic_viewer:
                self.epic_viewer.set_images(images)
        except Exception as e:
            self.notify(f"Failed to load epic images: {e}", title="API Error", severity="error")

    async def _update_iss(self) -> None:
        try:
            pos = await fetch_iss_position(self.client)
            if self.world_map:
                self.world_map.set_iss(pos.lat, pos.lon)
        except Exception as e:
            self.notify(f"Failed to update ISS position: {e}", title="API Error", severity="error")

    async def action_refresh(self) -> None:
        await self.refresh_all()

    def action_focus_panel(self, name: str) -> None:
        targets = {
            "map": self.world_map,
            "events": self.event_list,
            "tabs": self.asteroid_table,
        }
        w = targets.get(name)
        if w:
            w.focus()

    def action_help(self) -> None:
        self.notify(
            "q quit | r refresh | tab cycle | 1 map / 2 events / 3 tabs | arrows scroll",
            title="cosmo help",
            timeout=6,
        )

    def on_event_list_event_selected(self, message: EventList.EventSelected) -> None:
        if self.world_map:
            self.world_map.set_selected(message.event_id)
