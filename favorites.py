"""Persist and retrieve favorited characters."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from api import Character
from utils import FAVORITES_FILE


class FavoritesManager:
    """JSON-backed store for favorite characters."""

    MAX = 100

    def __init__(self) -> None:
        self._data: Dict[int, dict] = {}
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not FAVORITES_FILE.exists():
            return
        try:
            with open(FAVORITES_FILE) as f:
                raw: list = json.load(f)
            self._data = {item["id"]: item for item in raw if "id" in item}
        except (json.JSONDecodeError, OSError, KeyError):
            self._data = {}

    def _save(self) -> None:
        with open(FAVORITES_FILE, "w") as f:
            json.dump(list(self._data.values()), f, indent=2)

    # ── Operations ────────────────────────────────────────────────────────────

    def add(self, char: Character) -> bool:
        """Return ``True`` if newly added, ``False`` if already present."""
        if char.id in self._data:
            return False
        self._data[char.id] = char.to_dict()
        self._save()
        return True

    def remove(self, char_id: int) -> bool:
        """Return ``True`` if removed, ``False`` if not found."""
        if char_id not in self._data:
            return False
        del self._data[char_id]
        self._save()
        return True

    def toggle(self, char: Character) -> bool:
        """Add if absent, remove if present. Returns new state (True = now fav)."""
        if self.is_favorite(char.id):
            self.remove(char.id)
            return False
        else:
            self.add(char)
            return True

    def is_favorite(self, char_id: int) -> bool:
        return char_id in self._data

    def list(self) -> List[Character]:
        return [Character.from_dict(d) for d in self._data.values()]

    def get(self, char_id: int) -> Optional[Character]:
        d = self._data.get(char_id)
        return Character.from_dict(d) if d else None

    def count(self) -> int:
        return len(self._data)

    def clear(self) -> int:
        count = len(self._data)
        self._data.clear()
        self._save()
        return count


favorites = FavoritesManager()
