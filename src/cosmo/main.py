from __future__ import annotations

import argparse
import sys

from . import __version__
from .app import CosmoApp
from .config import Config
from .setup import first_run_setup, reset_key

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="cosmo", description="NASA Terminal Dashboard")
    p.add_argument("--reset-key", action="store_true", help="Re-enter NASA API key")
    p.add_argument("--use-demo-key", action="store_true", help="Use NASA DEMO_KEY")
    p.add_argument("--refresh", type=int, metavar="N", help="Refresh interval (seconds)")
    p.add_argument("--theme", choices=["default", "classic"], help="UI theme")
    p.add_argument("--version", action="version", version=f"cosmo {__version__}")
    return p.parse_args(argv)

def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.reset_key:
        reset_key()
        return 0

    cfg = Config.load()
    if cfg is None:
        cfg = first_run_setup(use_demo=args.use_demo_key)
    elif args.use_demo_key:
        cfg.api_key = "DEMO_KEY"

    if args.refresh:
        cfg.refresh_interval_seconds = max(30, args.refresh)
    
    if args.theme:
        cfg.theme = args.theme

    try:
        CosmoApp(cfg).run()
    except KeyboardInterrupt:
        return 130
    return 0

if __name__ == "__main__":
    sys.exit(run())
