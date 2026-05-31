import json
from pathlib import Path
from typing import Any

from config import PREFERENCES_FILE, DEFAULT_PREFERENCES, Theme, ScanMode


class Preferences:
    """Manages persistent user preferences stored in a JSON file."""

    def __init__(self) -> None:
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        """Load preferences from disk, falling back to defaults."""
        if PREFERENCES_FILE.exists():
            try:
                with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = self._merge(DEFAULT_PREFERENCES, loaded)
            except (json.JSONDecodeError, OSError):
                self._data = dict(DEFAULT_PREFERENCES)
        else:
            self._data = dict(DEFAULT_PREFERENCES)

    def save(self) -> None:
        """Persist current preferences to disk."""
        try:
            with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    @property
    def theme(self) -> str:
        return self._data.get("theme", Theme.SYSTEM.value)

    @theme.setter
    def theme(self, value: str) -> None:
        self._data["theme"] = value

    @property
    def last_folders(self) -> list[str]:
        return self._data.get("last_folders", [])

    @last_folders.setter
    def last_folders(self, value: list[str]) -> None:
        self._data["last_folders"] = value

    @property
    def scan_recursive(self) -> bool:
        return self._data.get("scan_recursive", True)

    @scan_recursive.setter
    def scan_recursive(self, value: bool) -> None:
        self._data["scan_recursive"] = value

    @property
    def scan_mode(self) -> str:
        return self._data.get("scan_mode", ScanMode.HASH.name)

    @scan_mode.setter
    def scan_mode(self, value: str) -> None:
        self._data["scan_mode"] = value

    @property
    def window(self) -> dict:
        return self._data.get("window", DEFAULT_PREFERENCES["window"])

    @window.setter
    def window(self, value: dict) -> None:
        self._data["window"] = value

    @staticmethod
    def _merge(defaults: dict, overrides: dict) -> dict:
        """Deep merge overrides into defaults."""
        result = dict(defaults)
        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Preferences._merge(result[key], value)
            else:
                result[key] = value
        return result