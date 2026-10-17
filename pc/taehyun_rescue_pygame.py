"""Windows launcher for the shared Pygame version."""
from pathlib import Path
import sys

ANDROID_SOURCE = Path(__file__).resolve().parents[1] / "android"
sys.path.insert(0, str(ANDROID_SOURCE))

from game_core import main

if __name__ == "__main__":
    raise SystemExit(main())
