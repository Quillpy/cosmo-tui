from __future__ import annotations

import json
import stat
from dataclasses import dataclass, asdict
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "cosmo"
DEMO_KEY = "DEMO_KEY"

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
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return None

    def save(self) -> None:
        p = config_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        try:
            p.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
