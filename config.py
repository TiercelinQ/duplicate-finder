from pathlib import Path
from enum import Enum, auto


APP_NAME = "Duplicate Finder"
APP_VERSION = "1.0.0"
ORG_NAME = "PersonalTools"

BASE_DIR = Path(__file__).resolve().parent
PREFERENCES_FILE = BASE_DIR / "preferences.json"

WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 800

SIDEBAR_MIN_WIDTH = 240

STATUSBAR_HEIGHT = 28
TOPBAR_HEIGHT = 48

SCAN_SECTION = "scan"
RESULTS_SECTION = "results"
SETTINGS_SECTION = "settings"

HASH_CHUNK_SIZE = 65536


class ScanMode(Enum):
    HASH = auto()
    NAME = auto()
    BOTH = auto()
    EITHER = auto()


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


DEFAULT_PREFERENCES: dict = {
    "theme": Theme.SYSTEM.value,
    "last_folders": [],
    "scan_recursive": True,
    "scan_mode": ScanMode.HASH.name,
    "window": {
        "width": WINDOW_DEFAULT_WIDTH,
        "height": WINDOW_DEFAULT_HEIGHT,
        "x": None,
        "y": None,
    },
}