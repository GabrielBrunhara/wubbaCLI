"""Mini-games using the Rick and Morty API."""
from __future__ import annotations

import json
import random
from typing import Dict


from api import Character, RickAndMortyAPI, APIError
from ascii_engine import image_url_to_ascii
from effects import console, reveal_ascii_art, _sleep
from settings import settings
from ui import (
    ask_play_again, show_error, show_game_header, show_game_result,
    show_multiple_choice, show_score_board, show_info, press_any_key,
)
from utils import SCORES_FILE


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

_GAME_ART_WIDTH = 80  # narrower art for game context so it fits beside the choices


def _fetch_char_with_art() -> tuple[Character, str]:
    """Fetch a random character and its ASCII art at game width."""
    char = RickAndMortyAPI.get_random_character()
    art = image_url_to_ascii(char.image, width=_GAME_ART_WIDTH)
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
    """Show ASCII art, pick the right name from 4 choices."""
    color = settings.color_theme

    while True:
        show_game_header(
            "GUESS WHO",
            f"Identify the character from their ASCII art  ·  {scores.session_result('Guess Who')}",
        )

        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        # Show art without name
        reveal_ascii_art(art, color, delay=0.008)
        console.print()

        # Build 4 choices
        wrong = _wrong_choices(char, 3)
        options = [char.name] + wrong
        random.shuffle(options)
        correct_idx = options.index(char.name)

        user_idx = show_multiple_choice(options, prompt="Who is this character?")
        correct = user_idx == correct_idx

        if correct:
            scores.add_win("Guess Who")
        else:
            scores.add_loss("Guess Who")

        show_game_result(correct, char.name, scores.all().get("Guess Who", {}).get("wins", 0), sum(scores.all().get("Guess Who", {}).values()))

        if not ask_play_again():
            break


# ── Alive or Dead ─────────────────────────────────────────────────────────────

def run_alive_or_dead() -> None:
    """Show art + info (no status), guess whether the character is alive."""
    color = settings.color_theme

    while True:
        show_game_header(
            "ALIVE OR DEAD",
            f"Is this character still in one piece?  ·  {scores.session_result('Alive or Dead')}",
        )

        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        reveal_ascii_art(art, color, delay=0.006)
        console.print()
        # Show everything EXCEPT status
        console.print(f"  [bold {color}]{char.name}[/bold {color}]  ·  {char.species}  ·  {char.gender}  ·  {char.origin}")
        console.print()

        options = ["Alive", "Dead", "Unknown"]
        user_idx = show_multiple_choice(options, prompt="What is their status?")
        user_answer = options[user_idx]

        # Normalise "unknown" comparison
        actual = char.status
        correct = user_answer.lower() == actual.lower()

        if correct:
            scores.add_win("Alive or Dead")
        else:
            scores.add_loss("Alive or Dead")

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
    """Show character name/art, guess the species."""
    color = settings.color_theme

    while True:
        show_game_header(
            "SPECIES ROULETTE",
            f"What species is this creature?  ·  {scores.session_result('Species Roulette')}",
        )

        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        reveal_ascii_art(art, color, delay=0.006)
        console.print()
        console.print(f"  [bold {color}]{char.name}[/bold {color}]  ·  {char.gender}  ·  {char.origin}")
        console.print()

        correct_species = char.species
        wrongs = [s for s in _SPECIES_POOL if s.lower() != correct_species.lower()]
        random.shuffle(wrongs)
        options = [correct_species] + wrongs[:3]
        random.shuffle(options)
        correct_idx = options.index(correct_species)

        user_idx = show_multiple_choice(options, prompt="What is their species?")
        correct = user_idx == correct_idx

        if correct:
            scores.add_win("Species Roulette")
        else:
            scores.add_loss("Species Roulette")

        stat = scores.all().get("Species Roulette", {})
        show_game_result(correct, correct_species, stat.get("wins", 0), stat.get("wins", 0) + stat.get("losses", 0))

        if not ask_play_again():
            break


# ── Episode Counter ───────────────────────────────────────────────────────────

def run_episode_counter() -> None:
    """Guess how many episodes a character appeared in (within ±3)."""
    color = settings.color_theme

    while True:
        show_game_header(
            "EPISODE COUNTER",
            f"How many episodes did this character appear in?  ·  {scores.session_result('Episode Counter')}",
        )

        try:
            char, art = _fetch_char_with_art()
        except APIError as exc:
            show_error(str(exc))
            return

        reveal_ascii_art(art, color, delay=0.006)
        console.print()
        console.print(
            f"  [bold {color}]{char.name}[/bold {color}]"
            f"  ·  {char.species}"
            f"  ·  [{char.status_color}]{char.status_icon} {char.status}[/{char.status_color}]"
        )
        console.print()

        actual = char.episode_count
        # Build 4 choices around the actual count
        diffs = random.sample([-5, -3, -2, -1, 1, 2, 3, 5], 3)
        options_raw = sorted(set([actual] + [max(1, actual + d) for d in diffs]))[:4]
        while len(options_raw) < 4:
            options_raw.append(max(1, actual + random.randint(6, 10)))
        options_raw = sorted(set(options_raw))[:4]
        options = [str(n) for n in options_raw]
        correct_idx = options.index(str(actual))

        user_idx = show_multiple_choice(options, prompt="Number of episodes?")
        correct = user_idx == correct_idx

        if correct:
            scores.add_win("Episode Counter")
        else:
            scores.add_loss("Episode Counter")

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
