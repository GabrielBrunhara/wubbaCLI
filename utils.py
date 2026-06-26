"""Shared path constants and small OS-level helpers."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Tuple

# ── Project root & data directories ──────────────────────────────────────────
ROOT: Path = Path(__file__).parent
CACHE_DIR: Path = ROOT / "ascii_cache"
EXPORTS_DIR: Path = ROOT / "exports"
FAVORITES_FILE: Path = ROOT / "favorites.json"
HISTORY_FILE: Path = ROOT / "history.json"
CONFIG_FILE: Path = ROOT / "config.json"
SCORES_FILE: Path = ROOT / "scores.json"


def ensure_dirs() -> None:
    """Create data directories that must exist before anything runs."""
    CACHE_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)


def get_terminal_size() -> Tuple[int, int]:
    """Return ``(columns, lines)`` of the current terminal."""
    s = shutil.get_terminal_size(fallback=(120, 40))
    return s.columns, s.lines


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def safe_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def truncate(text: str, max_len: int, suffix: str = "…") -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix
