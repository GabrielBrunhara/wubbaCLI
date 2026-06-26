"""Track every character the user has viewed, most-recent-first."""
from __future__ import annotations

import json
from typing import List

from api import Character
from utils import HISTORY_FILE


class HistoryManager:
    """Rolling list (newest first) of recently viewed characters."""

    MAX = 50

    def __init__(self) -> None:
        self._data: List[dict] = []
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not HISTORY_FILE.exists():
            return
        try:
            with open(HISTORY_FILE) as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._data = []

    def _save(self) -> None:
        with open(HISTORY_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    # ── Operations ────────────────────────────────────────────────────────────

    def add(self, char: Character) -> None:
        """Prepend to history, de-duplicate by id, cap at MAX."""
        entry = char.to_dict()
        # Remove existing entry for this character so it re-surfaces at top.
        self._data = [d for d in self._data if d.get("id") != char.id]
        self._data.insert(0, entry)
        self._data = self._data[: self.MAX]
        self._save()

    def list(self) -> List[Character]:
        return [Character.from_dict(d) for d in self._data]

    def clear(self) -> int:
        count = len(self._data)
        self._data.clear()
        self._save()
        return count

    def count(self) -> int:
        return len(self._data)


history = HistoryManager()
