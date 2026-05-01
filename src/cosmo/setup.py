from __future__ import annotations

import httpx
from .config import Config, config_path, DEMO_KEY

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
