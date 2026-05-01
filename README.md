<img width="1910" height="1033" alt="Screenshot" src="Screenshot.svg" />


# cosmo-tui

A terminal dashboard for NASA's open data. Real-time world map, asteroid tracker, ISS tracker, space weather, Mars rover photos, Earth imagery, and more — all in your terminal.

Built with [Textual](https://github.com/Textualize/textual) and [Rich](https://github.com/Textualize/rich).

## Features

- **ASCII World Map** — High-performance Braille-character world map with a spatial-grid optimization for smooth rendering.
- **Natural Event Tracking** — Wildfires, storms, earthquakes, volcanoes, floods from NASA's EONET API, plotted as color-coded markers on the map.
- **ISS Tracker & Pass Predictions** — Real-time ISS position plotted on the map + local pass predictions based on your **automatically detected location**.
- **Mars Weather** — Live environmental data (temperature, pressure, opacity) from the Curiosity rover's REMS instrument at Gale Crater.
- **NASA Media Search** — Instant search across NASA's Image and Video Library directly from your terminal.
- **Exoplanet Feed** — Real-time feed of the most recently confirmed planetary systems discovered beyond our solar system.
- **Mars Rover Photos** — Latest high-resolution photos from NASA's Perseverance and Curiosity rovers.
- **EPIC Earth Imagery** — Daily natural color imagery of the entire Earth captured by the DSCOVR satellite.
- **Wallpaper Export** — Save any APOD or EPIC image as a local wallpaper with a single keypress (`s`).
- **Space Weather** — Live monitor for solar flares, CMEs, and geomagnetic storms.
- **Theming Support** — Choose between a modern "Default" theme or a retro "Classic" monochrome green look.

### Map Legend

| Marker | Color | Meaning |
|--------|-------|---------|
| `●` | Red | Wildfires |
| `●` | Blue | Severe Storms |
| `●` | Yellow | Earthquakes |
| `●` | Orange | Volcanoes |
| `●` | Green | Floods |
| `★` | Bright Yellow | Fireball Impacts |
| `✦` | Bright Cyan | ISS Position |

## Installation

### From PyPI

```bash
pip install cosmo-tui
```

Or with [pipx](https://pipx.pypa.io/) (recommended for CLI tools):

```bash
pipx install cosmo-tui
```

### From Source

```bash
git clone https://github.com/irahulstomar/cosmo-tui.git
cd cosmo-tui
pip install -e .
```

## APIs & External Services

Cosmo aggregates data from several scientific and geographic services.

### 1. NASA Open Data (Requires API Key)
The core of the application relies on the official NASA API portal. You need one free API key to access most features.
*   **How to get it:**
    1. Go to **[https://api.nasa.gov](https://api.nasa.gov)**
    2. Sign up with your name and email.
    3. Your key will be emailed to you instantly.
*   **Used for:** APOD, Mars Rover Photos, EPIC Earth, Space Weather (DONKI), Near Earth Objects (NeoWs).

### 2. NASA Exoplanet Archive (No Key Required)
Queries the [TAP service](https://exoplanetarchive.ipac.caltech.edu/docs/TAP_usage.html) for the latest confirmed exoplanet discoveries.

### 3. NASA Image & Video Library (No Key Required)
Powers the **NASA Search** feature via `images-api.nasa.gov`.

### 4. MAAS2 Mars Weather (No Key Required)
Provides Curiosity rover environmental data via the [MAAS2 API](https://api.maas2.apollorion.com/).

### 5. ISS Tracking & Predictions (No Key Required)
*   **Tracking:** Uses TLE data from [TLE.ivanstanojevic.me](http://tle.ivanstanojevic.me/).
*   **Predictions:** Uses [Open Notify](http://open-notify.org/Open-Notify-API/ISS-Pass-Times/) to predict when the ISS will pass over your coordinates.

### 6. Geolocation (No Key Required)
Used once during app startup to detect your local Latitude/Longitude via [ip-api.com](https://ip-api.com/). This is strictly used to provide localized ISS pass predictions. No personal data is stored or transmitted.

## Usage

```bash
cosmo                    # Launch the dashboard
cosmo --theme classic    # Use retro green terminal theme
cosmo --use-demo-key     # Use NASA's rate-limited DEMO_KEY
cosmo --reset-key        # Re-enter your API key
cosmo --refresh 120      # Set refresh interval to 120 seconds (default: 300)
```

On first run, cosmo will prompt you to enter your NASA API key. It validates the key with a test API call, then saves it locally.

### Keybindings

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh all data |
| `s` | Save Image (in APOD/EPIC tabs) |
| `1` | Focus world map |
| `2` | Focus event list |
| `3` | Focus tab panels |
| `?` | Show help overlay |
| `Tab` | Cycle panel focus |
| `↑↓` | Scroll within active panel |

## Data Sources

| Panel | API | Update Frequency |
|-------|-----|-----------------|
| World Map + Events | [EONET v3](https://eonet.gsfc.nasa.gov/docs/v3) | Every refresh cycle |
| Mars Photos | [Mars Rover Photos](https://api.nasa.gov/#mars-photos) | Every refresh cycle |
| EPIC Earth | [EPIC API](https://api.nasa.gov/#epic) | Every refresh cycle |
| Asteroids | [NeoWs](https://api.nasa.gov/#asteroids-neows) | Every refresh cycle |
| Space Weather | [DONKI](https://api.nasa.gov/#donki) | Every refresh cycle |
| APOD | [APOD API](https://api.nasa.gov/#apod) | Every refresh cycle |
| Fireballs | [JPL Fireball API](https://ssd-api.jpl.nasa.gov/doc/fireball.html) | Every refresh cycle |
| Sentry Watch | [JPL Sentry API](https://ssd-api.jpl.nasa.gov/doc/sentry.html) | Every refresh cycle |
| ISS Position | [TLE API](http://tle.ivanstanojevic.me/) + SGP4 | Every 30 seconds |

## Requirements

- **Python 3.10+**
- A terminal with **Unicode** and **truecolor** support

### Supported Terminals

| Terminal | Support |
|----------|---------|
| Windows Terminal | Full |
| WezTerm | Full |
| iTerm2 (macOS) | Full |
| Kitty | Full |
| Most Linux terminals | Full |
| macOS Terminal.app | Partial (limited colors) |
| Windows cmd.exe | Not supported |

## Tech Stack

- **[Textual](https://github.com/Textualize/textual)** — TUI framework
- **[Rich](https://github.com/Textualize/rich)** — Terminal text formatting
- **[httpx](https://github.com/encode/httpx)** — Async HTTP client
- **[sgp4](https://github.com/brandon-rhodes/python-sgp4)** — Satellite orbit propagation (ISS tracking)
- **[platformdirs](https://github.com/platformdirs/platformdirs)** — Cross-platform config paths

## License

MIT
