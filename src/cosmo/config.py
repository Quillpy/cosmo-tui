from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass, asdict, field
from pathlib import Path

import httpx
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
        # Restrict config file to owner-only read/write (contains API key)
        try:
            p.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass  # Windows may not support Unix permissions


def validate_api_key(key: str, timeout: float = 10.0) -> bool:
    try:
        r = httpx.get(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": key},
            timeout=timeout,
        )
        return r.status_code == 200
    except httpx.HTTPError:
        return False


def first_run_setup(use_demo: bool = False) -> Config:
    print("\n\U0001F680  Welcome to Cosmo — NASA Terminal Dashboard\n")
    if use_demo:
        print("Using NASA DEMO_KEY (rate-limited).")
        cfg = Config(api_key=DEMO_KEY)
        cfg.save()
        print(f"\u2713 Config saved to {config_path()}\n")
        return cfg

    print("No API key found.")
    print("Get your free key at: https://api.nasa.gov\n")
    key = input("Enter your NASA API key (or press Enter to use DEMO_KEY): ").strip()
    if not key:
        key = DEMO_KEY
        print("Using DEMO_KEY.")
    else:
        # Sanitize: NASA API keys are alphanumeric only
        if not key.isalnum():
            print("\u2717 Invalid key format (must be alphanumeric). Falling back to DEMO_KEY.")
            key = DEMO_KEY
        else:
            print("Validating key...")
            if not validate_api_key(key):
                print("\u2717 Key validation failed. Falling back to DEMO_KEY.")
                key = DEMO_KEY
            else:
                print("\u2713 Key validated successfully.")

    cfg = Config(api_key=key)
    cfg.save()
    print(f"\u2713 Config saved to {config_path()}\n")
    return cfg


def reset_key() -> Config:
    p = config_path()
    if p.exists():
        p.unlink()
    return first_run_setup()
