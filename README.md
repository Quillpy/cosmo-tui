<img width="1910" height="1033" alt="Screenshot 2026-04-28 172727" src="https://github.com/user-attachments/assets/534a5566-d7b5-45b8-814d-e7be80b37e6d" />


# cosmo-tui

A terminal dashboard for NASA's open data. Real-time world map, asteroid tracker, ISS tracker, space weather, fireball events, impact risk monitor, and more — all in your terminal.

Built with [Textual](https://github.com/Textualize/textual) and [Rich](https://github.com/Textualize/rich).

## Features

- **ASCII World Map** — Braille-character world map rendered from Natural Earth land polygons with live event plotting
- **Natural Event Tracking** — Wildfires, storms, earthquakes, volcanoes, floods from NASA's EONET API, plotted as color-coded markers on the map
- **Event List** — Scrollable list synced with the map; select an event to highlight it
- **ISS Tracker** — Real-time International Space Station position plotted on the map, updated every 30 seconds using TLE + SGP4 orbital computation
- **Fireball Events** — Meteorite atmospheric impacts detected by US government sensors, plotted on the map
- **Asteroid Tracker** — Upcoming near-Earth object close approaches with size, miss distance, velocity, and hazard flags (NeoWs API)
- **Sentry Watch** — Impact risk monitor showing all NEOs with non-zero Earth impact probability, with Palermo and Torino scale ratings (JPL Sentry API)
- **Space Weather** — Solar flares, coronal mass ejections, geomagnetic storms, and solar energetic particles (DONKI API)
- **Astronomy Picture of the Day** — Daily APOD with title, explanation, and image link
- **Status Bar** — Live clock (local + UTC), last refresh time, countdown to next refresh, API rate quota, keyboard shortcuts, and a map legend

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

## Getting Your NASA API Key

Cosmo uses NASA's free public APIs. You'll need an API key (takes 30 seconds):

1. Go to **[https://api.nasa.gov](https://api.nasa.gov)**
2. Fill in your **First Name**, **Last Name**, and **Email**
3. Click **Sign Up**
4. Your API key will be **emailed to you instantly** and also shown on the page
5. Copy the key.

That's it. The key is free, gives you **1,000 requests per hour**, and never expires.

> **Don't want to sign up?** You can use NASA's public `DEMO_KEY` which works but is rate-limited to 30 requests/hour and 50/day. Run cosmo with `--use-demo-key` to use it.

## Usage

```bash
cosmo                    # Launch the dashboard
cosmo --use-demo-key     # Use NASA's rate-limited DEMO_KEY
cosmo --reset-key        # Re-enter your API key
cosmo --refresh 120      # Set refresh interval to 120 seconds (default: 300)
cosmo --version          # Show version
cosmo --help             # Show help
```

On first run, cosmo will prompt you to enter your NASA API key. It validates the key with a test API call, then saves it locally so you never have to enter it again.

### Where is my API key stored?

Your key is saved locally on your machine in a config file:

| OS | Path |
|----|------|
| Windows | `%LOCALAPPDATA%\cosmo\cosmo\config.json` |
| Linux | `~/.config/cosmo/config.json` |
| macOS | `~/Library/Application Support/cosmo/config.json` |

The file is set to owner-only permissions (`600`). Your key is **never** sent anywhere except to `api.nasa.gov`.

## Keybindings

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh all data |
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
