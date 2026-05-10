# Cosmo-TUI 🌌

[![PyPI version](https://badge.fury.io/py/cosmo-tui.svg)](https://badge.fury.io/py/cosmo-tui)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A terminal dashboard for NASA's open data. Real-time world map, asteroid tracker, space weather, Earth imagery, media search, and more — all in your terminal.

## Features

- **Live World Map** — Dot-matrix map using Braille characters, showing real-time natural events (wildfires, storms, volcanoes) and fireball impacts.
- **ISS Tracker** — Real-time ISS position plotted on the map.
- **Mars Weather** — Live environmental data (temperature, pressure, opacity) from the Curiosity rover's REMS instrument at Gale Crater.
- **Asteroid Monitor** — Track Near-Earth Objects (NEOs) and high-risk impact candidates via the JPL Sentry system.
- **Space Weather** — Live solar flares, geomagnetic storms, and CME reports.
- **Earth from Space** — Latest high-resolution imagery from the DSCOVR EPIC camera.
- **Astronomy Picture of the Day (APOD)** — Daily celestial imagery with full descriptions.
- **Exoplanet Discoveries** — Latest confirmed planets found outside our solar system.
- **NASA Media Search** — Search NASA's Image and Video Library from the TUI.

## Map Legend

| Marker | Color | Description |
|--------|-------|-------------|
| `●` | Category color | Natural Events (EONET) |
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
*   **Used for:** APOD, EPIC Earth, Space Weather (DONKI), Near Earth Objects (NeoWs).

### 2. NASA Exoplanet Archive (No Key Required)
Queries the [TAP service](https://exoplanetarchive.ipac.caltech.edu/docs/TAP_usage.html) for the latest confirmed exoplanet discoveries.

### 3. NASA Image & Video Library (No Key Required)
Powers the **NASA Search** feature via `images-api.nasa.gov`.

### 4. Curiosity Mars Weather (No Key Required)
Provides Curiosity rover environmental data at Gale Crater via [NASA's MSL Weather RSS feed](https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json).

### 5. ISS Tracking (No Key Required)
Uses TLE data from [TLE.ivanstanojevic.me](http://tle.ivanstanojevic.me/) and SGP4 for real-time orbital propagation.

## Usage

```bash
cosmo                    # Launch the dashboard
cosmo --theme classic    # Use retro green terminal theme
cosmo --use-demo-key     # Use NASA's rate-limited DEMO_KEY
cosmo --reset-key        # Re-enter your API key
cosmo --refresh 120      # Set refresh interval to 120 seconds (default: 300)
```

On first run, cosmo will prompt you to enter your NASA API key. It validates the key with a test API call, then saves it locally.

Configuration is stored in your platform config directory, for example `~/.config/cosmo/config.json` on many Linux systems. The file is written with user-only permissions where the operating system supports it.

### Keybindings

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh all data |
| `s` | Save image (APOD image entries and EPIC tab) |
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
| EPIC Earth | [EPIC API](https://api.nasa.gov/#epic) | Every refresh cycle |
| Asteroids | [NeoWs](https://api.nasa.gov/#asteroids-neows) | Every refresh cycle |
| Space Weather | [DONKI](https://api.nasa.gov/#donki) | Every refresh cycle |
| APOD | [APOD API](https://api.nasa.gov/#apod) | Every refresh cycle |
| Fireballs | [JPL Fireball API](https://ssd-api.jpl.nasa.gov/doc/fireball.html) | Every refresh cycle |
| Sentry Watch | [JPL Sentry API](https://ssd-api.jpl.nasa.gov/doc/sentry.html) | Every refresh cycle |
| ISS Position | [TLE API](http://tle.ivanstanojevic.me/) + SGP4 | Every 30 seconds |
| Exoplanets | [NASA Exoplanet Archive TAP](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html) | Every refresh cycle |
| NASA Search | [NASA Image and Video Library](https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf) | On demand |

## Requirements

- **Python 3.10+**
- A terminal with **Unicode** and **truecolor** support

### Supported Terminals

| Terminal | Support |
|----------|---------|
| iTerm2, Alacritty, Kitty, WezTerm | Full (Braille + Truecolor) |
| Windows Terminal, PowerShell | Full (Braille + Truecolor) |
| Apple Terminal.app | Partial (No truecolor) |
| Linux TTY / Console | Minimal (No Unicode) |

## License

Distributed under the MIT License. See `LICENSE` for more information.
