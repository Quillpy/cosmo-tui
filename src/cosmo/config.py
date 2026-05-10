from __future__ import annotations

import json
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "cosmo"
DEMO_KEY = "DEMO_KEY"
MIN_REFRESH_SECONDS = 30
VALID_THEMES = {"default", "classic"}

def config_path() -> Path:
    return Path(user_config_dir(APP_NAME)) / "config.json"

@dataclass
class Config:
    api_key: str = DEMO_KEY
    refresh_interval_seconds: int = 300
    theme: str = "default"

    @classmethod
    def load(cls) -> "Config | None":
        p = config_path()
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return None

            cfg = cls()
            api_key = data.get("api_key")
            if isinstance(api_key, str) and api_key.strip():
                cfg.api_key = api_key.strip()

            refresh = data.get("refresh_interval_seconds")
            if isinstance(refresh, int):
                cfg.refresh_interval_seconds = max(MIN_REFRESH_SECONDS, refresh)

            theme = data.get("theme")
            if isinstance(theme, str) and theme in VALID_THEMES:
                cfg.theme = theme
            return cfg
        except (OSError, json.JSONDecodeError):
            return None

    def save(self) -> None:
        p = config_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
            f.write("\n")
        try:
            p.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
