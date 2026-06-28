"""Mini-games using the Rick and Morty API."""
from __future__ import annotations

import json
import random
from typing import Dict


from api import Character, RickAndMortyAPI, APIError
from ascii_engine import image_url_to_ascii
from effects import _sleep
from settings import settings
from ui import (
    ask_play_again, show_error, show_game_result, show_game_screen,
    show_score_board, show_info, press_any_key,
)
from utils import clear_screen, SCORES_FILE


# ── Score tracker ─────────────────────────────────────────────────────────────

class ScoreTracker:
    """Persistent win/loss tracker for all games."""

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, int]] = {}
        self._load()

    def _load(self) -> None:
        if SCORES_FILE.exists():
            try:
                with open(SCORES_FILE) as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        with open(SCORES_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def _ensure(self, game: str) -> None:
        if game not in self._data:
            self._data[game] = {"wins": 0, "losses": 0}

    def add_win(self, game: str) -> None:
        self._ensure(game)
        self._data[game]["wins"] += 1
        self._save()

    def add_loss(self, game: str) -> None:
        self._ensure(game)
        self._data[game]["losses"] += 1
        self._save()

    def all(self) -> Dict:
        return dict(self._data)

    def session_result(self, game: str) -> str:
        d = self._data.get(game, {"wins": 0, "losses": 0})
        return f"W{d['wins']} / L{d['losses']}"


scores = ScoreTracker()


# ── Shared helpers ────────────────────────────────────────────────────────────

def _fetch_char_with_art() -> tuple[Character, str]:
    """Fetch a random character and ASCII art using the configured display width."""
    char = RickAndMortyAPI.get_random_character()
    art = image_url_to_ascii(char.image)
    return char, art


def _wrong_choices(correct: Character, count: int = 3) -> list[str]:
    """Return ``count`` wrong character names (distinct from correct)."""
    try:
        others = RickAndMortyAPI.get_random_characters(count + 2)
        names = [c.name for c in others if c.name != correct.name]
        return names[:count]
    except APIError:
        return [f"Morty #{i}" for i in range(count)]


# ── Guess Who ─────────────────────────────────────────────────────────────────

def run_guess_who() -> None:
    """Show ASCII art (no name), pick the right name from 4 choices."""
    while True:
        clear_screen()
        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        wrong = _wrong_choices(char, 3)
        options = [char.name] + wrong
        random.shuffle(options)
        correct_idx = options.index(char.name)

        info_rows = [
            ("Species",  char.species or "Unknown"),
            ("Gender",   char.gender),
            ("Origin",   char.origin),
            ("Episodes", str(char.episode_count)),
        ]
        user_idx = show_game_screen(
            art=art,
            title="GUESS WHO",
            subtitle=scores.session_result("Guess Who"),
            info_rows=info_rows,
            options=options,
            prompt="Who is this character?",
        )
        correct = user_idx == correct_idx
        scores.add_win("Guess Who") if correct else scores.add_loss("Guess Who")
        stat = scores.all().get("Guess Who", {})
        show_game_result(correct, char.name, stat.get("wins", 0), stat.get("wins", 0) + stat.get("losses", 0))

        if not ask_play_again():
            break


# ── Alive or Dead ─────────────────────────────────────────────────────────────

def run_alive_or_dead() -> None:
    """Show art + info (no status), guess whether the character is alive."""
    while True:
        clear_screen()
        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        options = ["Alive", "Dead", "Unknown"]
        info_rows = [
            ("Name",    char.name),
            ("Species", char.species or "Unknown"),
            ("Gender",  char.gender),
            ("Origin",  char.origin),
        ]
        user_idx = show_game_screen(
            art=art,
            title="ALIVE OR DEAD",
            subtitle=scores.session_result("Alive or Dead"),
            info_rows=info_rows,
            options=options,
            prompt="What is their status?",
        )
        actual = char.status
        correct = options[user_idx].lower() == actual.lower()
        scores.add_win("Alive or Dead") if correct else scores.add_loss("Alive or Dead")
        stat = scores.all().get("Alive or Dead", {})
        show_game_result(correct, actual, stat.get("wins", 0), stat.get("wins", 0) + stat.get("losses", 0))

        if not ask_play_again():
            break


# ── Species Roulette ──────────────────────────────────────────────────────────

_SPECIES_POOL = [
    "Human", "Alien", "Humanoid", "Poopybutthole",
    "Mythological Creature", "Animal", "Robot", "Cronenberg",
    "Disease", "Unknown",
]


def run_species_roulette() -> None:
    """Show art + name/info (no species), guess the species."""
    while True:
        clear_screen()
        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        correct_species = char.species
        wrongs = [s for s in _SPECIES_POOL if s.lower() != correct_species.lower()]
        random.shuffle(wrongs)
        options = [correct_species] + wrongs[:3]
        random.shuffle(options)
        correct_idx = options.index(correct_species)

        info_rows = [
            ("Name",   char.name),
            ("Gender", char.gender),
            ("Origin", char.origin),
            ("Status", f"{char.status_icon} {char.status}"),
        ]
        user_idx = show_game_screen(
            art=art,
            title="SPECIES ROULETTE",
            subtitle=scores.session_result("Species Roulette"),
            info_rows=info_rows,
            options=options,
            prompt="What is their species?",
        )
        correct = user_idx == correct_idx
        scores.add_win("Species Roulette") if correct else scores.add_loss("Species Roulette")
        stat = scores.all().get("Species Roulette", {})
        show_game_result(correct, correct_species, stat.get("wins", 0), stat.get("wins", 0) + stat.get("losses", 0))

        if not ask_play_again():
            break


# ── Episode Counter ───────────────────────────────────────────────────────────

def run_episode_counter() -> None:
    """Show art + info (no episode count), guess how many episodes."""
    while True:
        clear_screen()
        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        actual = char.episode_count
        diffs = random.sample([-5, -3, -2, -1, 1, 2, 3, 5], 3)
        options_raw = sorted(set([actual] + [max(1, actual + d) for d in diffs]))[:4]
        while len(options_raw) < 4:
            options_raw.append(max(1, actual + random.randint(6, 10)))
        options_raw = sorted(set(options_raw))[:4]
        options = [str(n) for n in options_raw]
        correct_idx = options.index(str(actual))

        info_rows = [
            ("Name",    char.name),
            ("Species", char.species or "Unknown"),
            ("Status",  f"{char.status_icon} {char.status}"),
            ("Gender",  char.gender),
        ]
        user_idx = show_game_screen(
            art=art,
            title="EPISODE COUNTER",
            subtitle=scores.session_result("Episode Counter"),
            info_rows=info_rows,
            options=options,
            prompt="How many episodes?",
        )
        correct = user_idx == correct_idx
        scores.add_win("Episode Counter") if correct else scores.add_loss("Episode Counter")
        stat = scores.all().get("Episode Counter", {})
        show_game_result(correct, str(actual), stat.get("wins", 0), stat.get("wins", 0) + stat.get("losses", 0))

        if not ask_play_again():
            break


# ── Score board ───────────────────────────────────────────────────────────────

def run_score_board() -> None:
    data = scores.all()
    if not data:
        show_info("No scores recorded yet. Play some games first!")
        press_any_key()
        return
    show_score_board(data)
    press_any_key()


# ── Surprise Me ───────────────────────────────────────────────────────────────

def run_surprise_me() -> None:
    """Randomly pick and run one of the available games."""
    games_pool = [
        run_guess_who,
        run_alive_or_dead,
        run_species_roulette,
        run_episode_counter,
    ]
    random.choice(games_pool)()
