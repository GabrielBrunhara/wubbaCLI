"""User-configurable settings backed by config.json."""
from __future__ import annotations

import json
from typing import Any, Dict

from utils import CONFIG_FILE

# ── Available options ─────────────────────────────────────────────────────────

CHARSETS: Dict[str, str] = {
    "detailed":  "@%#W$9876543210?!abc;:+=-,._ ",
    "simple":    "@#*+=-:. ",
    "blocks":    "█▓▒░ ",
    "binary":    "10 ",
    "dense":     "MWNXK0Okxdolc:;,. ",
    "matrix":    "ﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ01 ",
    "braille":   "⣿⣷⣯⣟⡿⢿⣻⣽⣾⡽⢻⡟⣛⡻⢛⡓⢓⡑⢑ ",
}

THEMES: Dict[str, str] = {
    "green":  "#00ff41",
    "cyan":   "#00e5ff",
    "amber":  "#ffb300",
    "red":    "#ff1744",
    "purple": "#e040fb",
    "white":  "#f5f5f5",
    "blue":   "#2979ff",
}

FIGLET_FONTS = [
    "ansi_shadow", "colossal", "banner3", "doom", "epic", "slant",
    "big", "block", "digital", "graffiti",
]

DEFAULTS: Dict[str, Any] = {
    "width":            100,
    "auto_width":       True,
    "charset":          "detailed",
    "color_theme":      "green",
    "figlet_font":      "ansi_shadow",
    "effects_enabled":  True,
    "typing_speed":     0.018,
    "animation_speed":  0.04,
    "matrix_duration":  3.5,
    "boot_style":       "epic",
}


# ── Settings class ────────────────────────────────────────────────────────────

class Settings:
    """Persistent settings with a simple property interface."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {**DEFAULTS}
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    self._data.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, fallback: Any = None) -> Any:
        return self._data.get(key, DEFAULTS.get(key, fallback))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def override(self, key: str, value: Any) -> None:
        """Change a value in memory only — not persisted to disk."""
        self._data[key] = value

    def reset(self) -> None:
        self._data = {**DEFAULTS}
        self.save()

    # ── Typed properties ──────────────────────────────────────────────────────

    @property
    def width(self) -> int:
        return int(self._data.get("width", 100))

    @property
    def auto_width(self) -> bool:
        return bool(self._data.get("auto_width", True))

    @property
    def display_width(self) -> int:
        """Effective width used when generating ASCII art for display."""
        if self.auto_width:
            import shutil
            cols, _ = shutil.get_terminal_size()
            return max(20, cols - 6)
        return self.width

    @property
    def charset_name(self) -> str:
        return self._data.get("charset", "detailed")

    @property
    def charset(self) -> str:
        return CHARSETS.get(self.charset_name, CHARSETS["detailed"])

    @property
    def color_theme_name(self) -> str:
        return self._data.get("color_theme", "green")

    @property
    def color_theme(self) -> str:
        return THEMES.get(self.color_theme_name, THEMES["green"])

    @property
    def figlet_font(self) -> str:
        return self._data.get("figlet_font", "ansi_shadow")

    @property
    def effects_enabled(self) -> bool:
        return bool(self._data.get("effects_enabled", True))

    @property
    def typing_speed(self) -> float:
        return float(self._data.get("typing_speed", 0.018))

    @property
    def animation_speed(self) -> float:
        return float(self._data.get("animation_speed", 0.04))

    @property
    def matrix_duration(self) -> float:
        return float(self._data.get("matrix_duration", 3.5))

    @property
    def boot_style(self) -> str:
        return str(self._data.get("boot_style", "epic"))


# ── Module-level singleton ────────────────────────────────────────────────────

settings = Settings()
