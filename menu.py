"""Main application — orchestrates all modes through a persistent menu loop."""
from __future__ import annotations

import os
import time
from typing import Optional

from rich.prompt import Prompt

from api import Character, Episode, RickAndMortyAPI, APIError
from ascii_engine import image_url_to_ascii
from cache import cache_stats, clear_cache
from effects import (
    console, reveal_ascii_art, typing_effect,
    show_pickle_rick, show_wubba_lubba, show_portal_secret,
    show_get_schwifty, show_szechuan_sauce, show_rickroll, _sleep,
    matrix_rain_reveal,
)
from export import export_html, export_txt
from favorites import favorites
from games import (
    run_alive_or_dead, run_episode_counter, run_guess_who,
    run_score_board, run_species_roulette, run_surprise_me,
)
from history import history
from settings import settings, CHARSETS, THEMES, FIGLET_FONTS
from ui import (
    OPACITY_CYCLE, confirm, press_any_key, show_character,
    show_character_action_prompt, show_character_list, show_character_stats,
    show_error, show_export_menu, show_games_menu, show_info, show_menu,
    show_search_results, show_settings, show_episode, show_success,
)
from explore import mode_explore
from utils import clear_screen


# ── Easter egg keyword map ────────────────────────────────────────────────────
_EASTER_EGGS = {
    "PICKLE RICK":          show_pickle_rick,
    "WUBBA LUBBA DUB DUB":  show_wubba_lubba,
    "PORTAL":               show_portal_secret,
    "GET SCHWIFTY":         show_get_schwifty,
    "SZECHUAN":             show_szechuan_sauce,
    "EVIL MORTY":           show_rickroll,
}


def _check_easter_egg(text: str) -> bool:
    key = text.strip().upper()
    fn = _EASTER_EGGS.get(key)
    if fn:
        fn()
        return True
    return False


# ── Character viewer (shared by several modes) ────────────────────────────────

def _view_character(char: Character) -> None:
    """Fetch ASCII art, display character, handle sub-actions (F/E/S/T/Q)."""
    history.add(char)

    art = image_url_to_ascii(char.image)
    is_fav = favorites.is_favorite(char.id)
    opacity_idx = 0  # starts at "dim" (50%)

    while True:
        clear_screen()
        show_character(char, art, is_fav, opacity=OPACITY_CYCLE[opacity_idx])

        action = show_character_action_prompt()

        if action == "T":
            opacity_idx = (opacity_idx + 1) % len(OPACITY_CYCLE)

        elif action == "F":
            is_fav = favorites.toggle(char)
            if is_fav:
                show_success(f"★  {char.name} added to favorites!")
            else:
                show_info(f"  {char.name} removed from favorites.")
            _sleep(0.7)

        elif action == "E":
            _export_mode(char, art)

        elif action == "S":
            from explore import _get_all_episodes
            try:
                all_eps = _get_all_episodes()
            except APIError:
                all_eps = None
            clear_screen()
            show_character_stats(char, all_episodes=all_eps)
            press_any_key()

        elif action in ("Q", "B"):
            break


# ── Export helper ─────────────────────────────────────────────────────────────

def _export_mode(char: Character, ascii_art: str) -> None:
    while True:
        clear_screen()
        choice = show_export_menu()

        if choice == "T":
            path = export_txt(char, ascii_art)
            show_success(f"Exported → {path}")
            press_any_key()
            break

        elif choice == "H":
            path = export_html(char, ascii_art)
            show_success(f"Exported → {path}")
            import webbrowser
            webbrowser.open(path.as_uri())
            press_any_key()
            break

        elif choice in ("Q", "B", ""):
            break


# ── Individual modes ──────────────────────────────────────────────────────────

def mode_classic() -> None:
    """A — Classic mode: exactly the original behavior, wrapped in Rich."""
    from pyfiglet import Figlet
    clear_screen()
    color = settings.color_theme
    try:
        char = RickAndMortyAPI.get_random_character()
    except APIError as exc:
        show_error(str(exc))
        press_any_key()
        return

    art = image_url_to_ascii(char.image)
    history.add(char)

    # Original figlet name print
    fig = Figlet(font=settings.figlet_font)
    name_art = fig.renderText(char.name)
    console.print(f"[bold {color}]{name_art}[/bold {color}]")

    reveal_ascii_art(art, color)
    press_any_key()


def mode_character_viewer(char: Optional[Character] = None) -> None:
    """B — Browse any character; if none passed, fetch a random one."""
    if char is None:
        clear_screen()
        color = settings.color_theme
        choice = Prompt.ask(
            f"  [bold {color}]Enter character ID (or press Enter for random)[/bold {color}]"
        ).strip()
        try:
            if choice:
                char = RickAndMortyAPI.get_character(int(choice))
            else:
                char = RickAndMortyAPI.get_random_character()
        except APIError as exc:
            show_error(str(exc))
            press_any_key()
            return
        except ValueError:
            show_error("Invalid ID. Please enter a number.")
            press_any_key()
            return

    _view_character(char)


def mode_search() -> None:
    """G — Search characters by name."""
    clear_screen()
    color = settings.color_theme
    query = Prompt.ask(f"  [bold {color}]Search character name[/bold {color}]").strip()
    if not query:
        return

    if _check_easter_egg(query):
        press_any_key()
        return

    try:
        results = RickAndMortyAPI.search_characters(query)
    except APIError as exc:
        show_error(str(exc))
        press_any_key()
        return

    if not results:
        show_error(f"No characters found for '{query}'.")
        press_any_key()
        return

    if len(results) == 1:
        _view_character(results[0])
        return

    idx = show_search_results(results)
    if idx is not None:
        _view_character(results[idx])


def mode_random_episode() -> None:
    """H — Show a random episode, let user open any character in it."""
    clear_screen()
    try:
        episode = RickAndMortyAPI.get_random_episode()
    except APIError as exc:
        show_error(str(exc))
        press_any_key()
        return

    # Fetch up to 20 characters from the episode
    ids = episode.character_ids[:20]
    try:
        chars = RickAndMortyAPI.get_multiple_characters(ids)
    except APIError:
        chars = []

    while True:
        clear_screen()
        show_episode(episode, chars)
        raw = Prompt.ask(
            f"  [bold {settings.color_theme}]Number to open character (or Q)[/bold {settings.color_theme}]"
        ).strip()

        if raw.upper() in ("Q", "B", ""):
            break

        try:
            idx = int(raw) - 1
            if 0 <= idx < len(chars):
                _view_character(chars[idx])
            else:
                show_error("Number out of range.")
                _sleep(0.8)
        except ValueError:
            show_error("Enter a valid number.")
            _sleep(0.8)


def mode_character_stats() -> None:
    """I — Deep stats for any character."""
    clear_screen()
    color = settings.color_theme
    choice = Prompt.ask(
        f"  [bold {color}]Enter character ID (or Enter for random)[/bold {color}]"
    ).strip()
    try:
        if choice:
            char = RickAndMortyAPI.get_character(int(choice))
        else:
            char = RickAndMortyAPI.get_random_character()
    except APIError as exc:
        show_error(str(exc))
        press_any_key()
        return
    except ValueError:
        show_error("Invalid ID.")
        press_any_key()
        return

    clear_screen()
    show_character_stats(char)
    press_any_key()


def mode_favorites() -> None:
    """J — View and open favorited characters."""
    while True:
        clear_screen()
        chars = favorites.list()
        idx = show_character_list(chars, f"Favorites  ({len(chars)})")
        if idx is None:
            break
        _view_character(chars[idx])


def mode_history() -> None:
    """K — View recently seen characters."""
    while True:
        clear_screen()
        chars = history.list()
        idx = show_character_list(chars, f"History  ({len(chars)} entries)")
        if idx is None:
            break
        _view_character(chars[idx])


def mode_games() -> None:
    """G — Games and trivia submenu."""
    while True:
        clear_screen()
        choice = show_games_menu()
        if choice == "G":
            run_guess_who()
        elif choice == "A":
            run_alive_or_dead()
        elif choice == "S":
            run_species_roulette()
        elif choice == "E":
            run_episode_counter()
        elif choice == "R":
            run_surprise_me()
        elif choice == "P":
            clear_screen()
            run_score_board()
            press_any_key()
        elif choice == "Q":
            break


def mode_matrix_reveal() -> None:
    """R — ASCII art emerges from the matrix rain; rain holds until Enter."""
    import shutil
    from cache import get_image
    clear_screen()
    try:
        char = RickAndMortyAPI.get_random_character()
    except APIError as exc:
        show_error(str(exc))
        press_any_key()
        return

    term_cols, term_rows = shutil.get_terminal_size()
    img = get_image(char.image)
    img_w, img_h = img.size
    max_w_for_height = int((term_rows - 6) / ((img_h / img_w) * 0.55))
    matrix_width = max(20, min(settings.width, term_cols - 4, max_w_for_height))
    art = image_url_to_ascii(char.image, width=matrix_width)

    matrix_rain_reveal(art)
    _view_character(char)


def mode_settings() -> None:
    """M — Settings panel with live preview."""
    while True:
        clear_screen()
        choice = show_settings(settings)

        if choice == "W":
            color = settings.color_theme
            raw = Prompt.ask(
                f"  [bold {color}]New width (current: {settings.width}, range 40-300)[/bold {color}]"
            ).strip()
            try:
                w = int(raw)
                if 40 <= w <= 300:
                    settings.set("width", w)
                    show_success(f"Width set to {w}.")
                else:
                    show_error("Must be between 40 and 300.")
            except ValueError:
                show_error("Enter a valid number.")
            _sleep(0.8)

        elif choice == "C":
            _pick_charset()

        elif choice == "T":
            _pick_color_theme()

        elif choice == "F":
            _pick_figlet_font()

        elif choice == "A":
            new_val = not settings.auto_width
            settings.set("auto_width", new_val)
            show_success(f"Auto Width {'enabled' if new_val else 'disabled'}.")
            _sleep(0.8)

        elif choice == "B":
            new_val = "classic" if settings.boot_style == "epic" else "epic"
            settings.set("boot_style", new_val)
            show_success(f"Boot Style set to '{new_val}'.")
            _sleep(0.8)

        elif choice == "E":
            new_val = not settings.effects_enabled
            settings.set("effects_enabled", new_val)
            show_success(f"Effects {'enabled' if new_val else 'disabled'}.")
            _sleep(0.8)

        elif choice == "S":
            color = settings.color_theme
            raw = Prompt.ask(
                f"  [bold {color}]Typing speed in seconds (current: {settings.typing_speed})[/bold {color}]"
            ).strip()
            try:
                v = float(raw)
                if 0 <= v <= 0.2:
                    settings.set("typing_speed", v)
                    show_success(f"Speed set to {v}s per character.")
                else:
                    show_error("Enter a value between 0 and 0.2.")
            except ValueError:
                show_error("Invalid number.")
            _sleep(0.8)

        elif choice == "R":
            if confirm("Reset all settings to defaults?"):
                settings.reset()
                show_success("Settings reset to defaults.")
            _sleep(0.8)

        elif choice == "X":
            stats = cache_stats()
            if confirm(f"Clear {stats['count']} cached images ({stats['size_mb']} MB)?"):
                removed = clear_cache()
                show_success(f"Removed {removed} cached images.")
            _sleep(0.8)

        elif choice in ("Q", "B", ""):
            break


def _pick_color_theme() -> None:
    """Color theme picker — each name rendered in its own colour."""
    color = settings.color_theme
    console.print()
    for i, (name, hex_val) in enumerate(THEMES.items(), 1):
        marker = f"  [dim {color}]◄[/dim {color}]" if name == settings.color_theme_name else ""
        console.print(f"  [{color}]{i:2}[/{color}]  [{hex_val}]■  {name}[/{hex_val}]{marker}")
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Pick Color Theme (number)[/bold {color}]").strip()
    try:
        names = list(THEMES.keys())
        idx = int(raw) - 1
        if 0 <= idx < len(names):
            settings.set("color_theme", names[idx])
            show_success(f"Color Theme set to '{names[idx]}'.")
        else:
            show_error("Out of range.")
    except ValueError:
        show_error("Invalid number.")
    _sleep(0.8)


def _pick_charset() -> None:
    """Charset picker — shows the actual chars as a preview."""
    color = settings.color_theme
    names = list(CHARSETS.keys())
    console.print()
    for i, name in enumerate(names, 1):
        marker = f"  [dim {color}]◄[/dim {color}]" if name == settings.charset_name else ""
        console.print(
            f"  [{color}]{i:2}[/{color}]  [bold {color}]{name:<10}[/bold {color}]"
            f"  [dim {color}]{CHARSETS[name]}[/dim {color}]{marker}"
        )
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Pick Charset (number)[/bold {color}]").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(names):
            settings.set("charset", names[idx])
            show_success(f"Charset set to '{names[idx]}'.")
        else:
            show_error("Out of range.")
    except ValueError:
        show_error("Invalid number.")
    _sleep(0.8)


def _pick_figlet_font() -> None:
    """Figlet font picker — renders 'C137' as a live sample for each font."""
    from pyfiglet import Figlet
    from rich.text import Text as _Text
    color = settings.color_theme
    clear_screen()
    console.print()
    for i, font in enumerate(FIGLET_FONTS, 1):
        header = _Text()
        header.append(f"  {i:2}  ", style=f"bold {color}")
        header.append(font, style=f"bold {color}")
        if font == settings.figlet_font:
            header.append("  ◄", style=f"dim {color}")
        console.print(header)
        try:
            sample = Figlet(font=font).renderText("C137")
            lines = [l for l in sample.split("\n") if l.strip()]
            for line in lines:
                console.print(_Text("       " + line, style=f"dim {color}"))
        except Exception:
            pass
        console.print()
    raw = Prompt.ask(f"  [bold {color}]Pick Figlet Font (number)[/bold {color}]").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(FIGLET_FONTS):
            settings.set("figlet_font", FIGLET_FONTS[idx])
            show_success(f"Figlet Font set to '{FIGLET_FONTS[idx]}'.")
        else:
            show_error("Out of range.")
    except ValueError:
        show_error("Invalid number.")
    _sleep(0.8)


def _pick_from_list(setting_key: str, options: list, label: str) -> None:
    """Helper: show numbered list, set setting by index."""
    color = settings.color_theme
    console.print()
    for i, opt in enumerate(options, 1):
        console.print(f"  [{color}]{i:2}[/{color}]  {opt}")
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Pick {label} (number)[/bold {color}]").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            settings.set(setting_key, options[idx])
            show_success(f"{label} set to '{options[idx]}'.")
        else:
            show_error("Out of range.")
    except ValueError:
        show_error("Invalid number.")
    _sleep(0.8)


# ── Main loop ─────────────────────────────────────────────────────────────────

_DISPATCH = {
    "C": mode_character_viewer,
    "B": mode_search,
    "E": mode_random_episode,
    "M": mode_matrix_reveal,
    "G": mode_games,
    "F": mode_favorites,
    "H": mode_history,
    "X": mode_explore,
    "S": mode_settings,
}


def run_app() -> None:
    """Start and run the main menu loop."""
    while True:
        clear_screen()
        raw = show_menu()

        if not raw:
            continue

        if raw == "Q":
            clear_screen()
            typing_effect("  Wubba lubba dub dub!", settings.color_theme, delay=0.04)
            _sleep(0.8)
            break

        fn = _DISPATCH.get(raw)
        if fn:
            try:
                fn()
            except KeyboardInterrupt:
                pass
            except APIError as exc:
                show_error(str(exc))
                press_any_key()
        else:
            show_error(f"Unknown option: {raw}")
            _sleep(0.6)


def _export_pick() -> None:
    """Choose a character to export, then export it."""
    clear_screen()
    color = settings.color_theme
    choice = Prompt.ask(
        f"  [bold {color}]Enter character ID to export (or Enter for random)[/bold {color}]"
    ).strip()
    try:
        if choice:
            char = RickAndMortyAPI.get_character(int(choice))
        else:
            char = RickAndMortyAPI.get_random_character()
    except (APIError, ValueError) as exc:
        show_error(str(exc))
        press_any_key()
        return

    art = image_url_to_ascii(char.image)
    _export_mode(char, art)
