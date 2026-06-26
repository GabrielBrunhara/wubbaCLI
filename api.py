"""Rick and Morty API client — typed, cached session, clean error surface."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

import requests


BASE_URL = "https://rickandmortyapi.com/api"


# ── Errors ────────────────────────────────────────────────────────────────────

class APIError(Exception):
    """Raised for any network or API-level failure."""


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class Character:
    id: int
    name: str
    status: str      # Alive | Dead | unknown
    species: str
    type: str
    gender: str
    origin: str
    location: str
    image: str
    episodes: List[str]
    url: str
    created: str

    # ── Derived ───────────────────────────────────────────────────────────────

    @property
    def episode_count(self) -> int:
        return len(self.episodes)

    @property
    def status_color(self) -> str:
        return {"Alive": "green", "Dead": "red"}.get(self.status, "yellow")

    @property
    def status_icon(self) -> str:
        return {"Alive": "●", "Dead": "✖", "unknown": "?"}.get(self.status, "?")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "status": self.status,
            "species": self.species, "type": self.type, "gender": self.gender,
            "origin": self.origin, "location": self.location,
            "image": self.image, "episodes": self.episodes,
            "url": self.url, "created": self.created,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Character":
        return cls(
            id=d["id"],
            name=d["name"],
            status=d["status"],
            species=d["species"],
            type=d.get("type", ""),
            gender=d["gender"],
            origin=d["origin"]["name"] if isinstance(d["origin"], dict) else d["origin"],
            location=d["location"]["name"] if isinstance(d["location"], dict) else d["location"],
            image=d["image"],
            episodes=d.get("episodes", d.get("episode", [])),
            url=d["url"],
            created=d["created"],
        )


@dataclass
class Episode:
    id: int
    name: str
    air_date: str
    episode: str     # e.g. S01E04
    characters: List[str]
    url: str

    @property
    def character_count(self) -> int:
        return len(self.characters)

    @property
    def character_ids(self) -> List[int]:
        return [int(u.rstrip("/").split("/")[-1]) for u in self.characters]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Episode":
        return cls(
            id=d["id"],
            name=d["name"],
            air_date=d["air_date"],
            episode=d["episode"],
            characters=d.get("characters", d.get("character", [])),
            url=d["url"],
        )


# ── API client ────────────────────────────────────────────────────────────────

class RickAndMortyAPI:
    _session: ClassVar[Optional[requests.Session]] = None

    @classmethod
    def _get_session(cls) -> requests.Session:
        if cls._session is None:
            cls._session = requests.Session()
            cls._session.headers.update({"User-Agent": "RickTerminal/2.0"})
        return cls._session

    @classmethod
    def _get(cls, path: str, params: Optional[Dict] = None) -> Any:
        try:
            r = cls._get_session().get(f"{BASE_URL}/{path}", params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.ConnectionError:
            raise APIError("No internet connection. Check your network.")
        except requests.Timeout:
            raise APIError("Request timed out — the API may be overwhelmed.")
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "?"
            if code == 404:
                raise APIError("Resource not found (404).")
            raise APIError(f"API returned HTTP {code}.")

    # ── Characters ────────────────────────────────────────────────────────────

    @classmethod
    def get_character(cls, cid: int) -> Character:
        return Character.from_dict(cls._get(f"character/{cid}"))

    @classmethod
    def get_random_character(cls) -> Character:
        total = cls._get("character")["info"]["count"]
        return cls.get_character(random.randint(1, total))

    @classmethod
    def get_total_characters(cls) -> int:
        return cls._get("character")["info"]["count"]

    @classmethod
    def search_characters(cls, name: str) -> List[Character]:
        try:
            data = cls._get("character", params={"name": name})
        except APIError:
            return []
        results: List[Dict] = data["results"]
        while data["info"]["next"]:
            data = cls._get_session().get(data["info"]["next"], timeout=10).json()
            results.extend(data["results"])
        return [Character.from_dict(c) for c in results]

    @classmethod
    def get_multiple_characters(cls, ids: List[int]) -> List[Character]:
        if not ids:
            return []
        if len(ids) == 1:
            return [cls.get_character(ids[0])]
        data = cls._get(f"character/{','.join(map(str, ids))}")
        if isinstance(data, dict):
            return [Character.from_dict(data)]
        return [Character.from_dict(c) for c in data]

    @classmethod
    def get_random_characters(cls, count: int = 4) -> List[Character]:
        total = cls.get_total_characters()
        ids = random.sample(range(1, total + 1), min(count, total))
        return cls.get_multiple_characters(ids)

    # ── Episodes ──────────────────────────────────────────────────────────────

    @classmethod
    def get_episode(cls, eid: int) -> Episode:
        return Episode.from_dict(cls._get(f"episode/{eid}"))

    @classmethod
    def get_random_episode(cls) -> Episode:
        total = cls._get("episode")["info"]["count"]
        return Episode.from_dict(cls._get(f"episode/{random.randint(1, total)}"))
