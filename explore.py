"""All 'Explore the Universe' mode functions."""
from __future__ import annotations

from collections import Counter
from typing import List, Optional

from api import Character, Episode, Location, RickAndMortyAPI, APIError
from ascii_engine import image_url_to_ascii
from effects import _sleep
from settings import settings
from ui import (
    console, press_any_key, show_error, show_info, show_success,
    show_location, show_location_list, show_dimension_list,
    show_census, show_season_list, show_season_episodes,
    show_leaderboard, show_dead_roster,
    show_character, show_character_action_prompt,
    show_explore_menu, OPACITY_CYCLE,
)
from utils import clear_screen

from rich.prompt import Prompt
from rich.status import Status


# ── Shared universe cache (loaded once per session) ───────────────────────────

_universe: Optional[List[Character]] = None
_all_episodes: Optional[List[Episode]] = None
_all_locations: Optional[List[Location]] = None


def _get_universe() -> List[Character]:
    global _universe
    if _universe is None:
        color = settings.color_theme
        with Status(f"  [{color}]Scanning the multiverse…[/{color}]"):
            _universe = RickAndMortyAPI.get_all_characters()
    return _universe


def _get_all_episodes() -> List[Episode]:
    global _all_episodes
    if _all_episodes is None:
        color = settings.color_theme
        with Status(f"  [{color}]Loading episode archive…[/{color}]"):
            _all_episodes = RickAndMortyAPI.get_all_episodes()
    return _all_episodes


def _get_all_locations() -> List[Location]:
    global _all_locations
    if _all_locations is None:
        color = settings.color_theme
        with Status(f"  [{color}]Mapping the multiverse…[/{color}]"):
            _all_locations = RickAndMortyAPI.get_all_locations()
    return _all_locations


# ── Internal character viewer (used by all explore modes) ─────────────────────

def _view_character(char: Character) -> None:
    from favorites import favorites
    from history import history
    history.add(char)
    art = image_url_to_ascii(char.image)
    is_fav = favorites.is_favorite(char.id)
    opacity_idx = 0
    while True:
        clear_screen()
        show_character(char, art, is_fav, opacity=OPACITY_CYCLE[opacity_idx])
        action = show_character_action_prompt()
        if action == "T":
            opacity_idx = (opacity_idx + 1) % len(OPACITY_CYCLE)
        elif action == "F":
            is_fav = favorites.toggle(char)
            show_success(f"{'★ Added' if is_fav else 'Removed'}: {char.name}")
            _sleep(0.7)
        elif action == "E":
            _export(char, art)
        elif action == "S":
            from ui import show_character_stats
            try:
                all_eps = _get_all_episodes()
            except APIError:
                all_eps = None
            clear_screen()
            show_character_stats(char, all_episodes=all_eps)
            press_any_key()
        elif action in ("Q", "B"):
            break


def _export(char: Character, art: str) -> None:
    from export import export_html, export_txt
    from ui import show_export_menu
    import webbrowser
    while True:
        clear_screen()
        choice = show_export_menu()
        if choice == "T":
            p = export_txt(char, art)
            show_success(f"Exported → {p}")
            press_any_key()
            break
        elif choice == "H":
            p = export_html(char, art)
            show_success(f"Exported → {p}")
            webbrowser.open(p.as_uri())
            press_any_key()
            break
        elif choice in ("Q", "B", ""):
            break


# ── 1. Location Explorer ───────────────────────────────────────────────────────

def mode_location_explorer() -> None:
    color = settings.color_theme
    try:
        locations = _get_all_locations()
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    while True:
        clear_screen()
        console.print()
        query = Prompt.ask(
            f"  [{color}]Filter by name/dimension/type (Enter for all)[/{color}]"
        ).strip().lower()

        filtered = [
            l for l in locations
            if not query or query in l.name.lower()
            or query in l.dimension.lower() or query in l.type.lower()
        ]
        if not filtered:
            show_error("No locations matched."); _sleep(0.8); continue

        idx = show_location_list(filtered, f"Locations ({len(filtered)})")
        if idx is None:
            break

        loc = filtered[idx]
        clear_screen()
        try:
            residents: List[Character] = []
            if loc.resident_ids:
                residents = RickAndMortyAPI.get_multiple_characters(loc.resident_ids[:30])
        except APIError:
            residents = []

        while True:
            clear_screen()
            show_location(loc, residents)
            raw = Prompt.ask(
                f"  [bold {color}]Number to open resident (or Q)[/bold {color}]"
            ).strip()
            if raw.upper() in ("Q", "B", ""):
                break
            try:
                i = int(raw) - 1
                if 0 <= i < len(residents):
                    _view_character(residents[i])
                else:
                    show_error("Out of range."); _sleep(0.7)
            except ValueError:
                show_error("Enter a valid number."); _sleep(0.7)


# ── 2. Dimension Atlas ─────────────────────────────────────────────────────────

def mode_dimension_atlas() -> None:
    try:
        locations = _get_all_locations()
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    # Group by dimension
    dim_map: dict = {}
    for loc in locations:
        key = loc.dimension
        if key not in dim_map:
            dim_map[key] = []
        dim_map[key].append(loc)

    dims = sorted(
        [(d, len(locs), sum(l.resident_count for l in locs)) for d, locs in dim_map.items()],
        key=lambda x: x[1], reverse=True,
    )

    while True:
        clear_screen()
        idx = show_dimension_list(dims)
        if idx is None:
            break

        dim_name, _, _ = dims[idx]
        dim_locs = sorted(dim_map[dim_name], key=lambda l: l.resident_count, reverse=True)

        while True:
            clear_screen()
            loc_idx = show_location_list(dim_locs, f"Dimension: {dim_name}")
            if loc_idx is None:
                break
            loc = dim_locs[loc_idx]
            try:
                residents = RickAndMortyAPI.get_multiple_characters(loc.resident_ids[:30]) if loc.resident_ids else []
            except APIError:
                residents = []

            while True:
                clear_screen()
                show_location(loc, residents)
                raw = Prompt.ask(
                    f"  [bold {settings.color_theme}]Number to open (or Q)[/bold {settings.color_theme}]"
                ).strip()
                if raw.upper() in ("Q", "B", ""):
                    break
                try:
                    i = int(raw) - 1
                    if 0 <= i < len(residents):
                        _view_character(residents[i])
                    else:
                        show_error("Out of range."); _sleep(0.7)
                except ValueError:
                    show_error("Enter a valid number."); _sleep(0.7)


# ── 3. Universe Census ─────────────────────────────────────────────────────────

def mode_census() -> None:
    try:
        chars = _get_universe()
        locs  = _get_all_locations()
        eps   = _get_all_episodes()
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    status_counts = Counter(c.status.lower() for c in chars)
    species_count = Counter(c.species for c in chars)
    gender_count  = Counter(c.gender.lower() for c in chars)
    loc_count     = Counter(c.location for c in chars)

    stats = {
        "total_chars": len(chars),
        "total_locs":  len(locs),
        "total_eps":   len(eps),
        "alive":       status_counts.get("alive", 0),
        "dead":        status_counts.get("dead", 0),
        "unknown":     status_counts.get("unknown", 0),
        "species":     species_count.most_common(10),
        "gender":      dict(gender_count.most_common()),
        "locations":   loc_count.most_common(8),
    }

    clear_screen()
    show_census(stats)
    press_any_key()


# ── 4. Season Breakdown ────────────────────────────────────────────────────────

def mode_season_breakdown() -> None:
    try:
        all_eps = _get_all_episodes()
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    # Group by season code prefix
    season_map: dict = {}
    for ep in all_eps:
        s = ep.episode[:3]  # "S01", "S02", …
        season_map.setdefault(s, []).append(ep)

    seasons = sorted(
        [(f"Season {int(k[1:])}", v) for k, v in season_map.items()],
        key=lambda x: x[0],
    )

    while True:
        clear_screen()
        s_idx = show_season_list(seasons)
        if s_idx is None:
            break

        s_label, s_eps = seasons[s_idx]
        while True:
            clear_screen()
            ep_idx = show_season_episodes(s_label, s_eps)
            if ep_idx is None:
                break
            _run_cast_roll(s_eps[ep_idx])


# ── 5. Episode Cast Roll ───────────────────────────────────────────────────────

def _run_cast_roll(episode: Episode) -> None:
    color = settings.color_theme
    try:
        chars = RickAndMortyAPI.get_multiple_characters(episode.character_ids)
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    if not chars:
        show_info("No characters found for this episode."); press_any_key(); return

    for i, char in enumerate(chars):
        clear_screen()
        art = image_url_to_ascii(char.image)
        console.print()
        from ui import _divider, _info_table
        from rich.panel import Panel
        from rich.columns import Columns
        from rich.text import Text
        _divider(f"  {episode.episode} — {episode.name}  [{i+1}/{len(chars)}]  ")

        ascii_text = Text(art, style=f"dim {color}", overflow="fold", no_wrap=True)
        ascii_panel = Panel(ascii_text, border_style=color, padding=(0, 1))

        info_rows = [
            ("Name",     char.name),
            ("Status",   f"{char.status_icon} {char.status}"),
            ("Species",  char.species or "Unknown"),
            ("Gender",   char.gender),
            ("Origin",   char.origin),
            ("Location", char.location),
        ]
        info_panel = Panel(
            _info_table(info_rows, color),
            title=f"[bold {color}]{char.name}[/bold {color}]",
            border_style=color, padding=(1, 2),
        )
        console.print(Columns([ascii_panel, info_panel], equal=False, expand=True))
        console.print()
        console.print(
            f"  [dim][{color}]N[/{color}] next  "
            f"[{color}]O[/{color}] open character  "
            f"[{color}]Q[/{color}] stop[/dim]"
        )
        console.print()
        console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
        console.file.flush()
        from ui import getch
        key = getch({"N", "O", "Q"})
        if key == "Q":
            break
        if key == "O":
            _view_character(char)


# ── 6. Most Wanted Leaderboard ────────────────────────────────────────────────

def mode_leaderboard() -> None:
    try:
        chars = _get_universe()
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    clear_screen()
    show_leaderboard(chars)
    press_any_key()


# ── 8. Dead Roster ────────────────────────────────────────────────────────────

def mode_dead_roster() -> None:
    color = settings.color_theme
    try:
        with Status(f"  [{color}]Counting the dead…[/{color}]"):
            dead = RickAndMortyAPI.get_all_characters(status="dead")
    except APIError as exc:
        show_error(str(exc)); press_any_key(); return

    dead.sort(key=lambda c: c.name)
    page = 0
    per_page = 25
    total_pages = (len(dead) - 1) // per_page + 1

    while True:
        clear_screen()
        result = show_dead_roster(dead, page, per_page)
        if result is None:
            break
        elif result == -999:
            _sleep(0.5)
        elif result < 0:
            # Encoded page navigation
            new_page = -result - 1
            page = max(0, min(new_page, total_pages - 1))
        else:
            _view_character(dead[result])


# ── Explore submenu dispatcher ────────────────────────────────────────────────

def mode_explore() -> None:
    _EXPLORE_DISPATCH = {
        "L": mode_location_explorer,
        "D": mode_dimension_atlas,
        "N": mode_census,
        "S": mode_season_breakdown,
        "W": mode_leaderboard,
        "K": mode_dead_roster,
    }
    while True:
        clear_screen()
        choice = show_explore_menu()
        if choice == "Q":
            break
        fn = _EXPLORE_DISPATCH.get(choice)
        if fn:
            try:
                fn()
            except KeyboardInterrupt:
                pass
            except APIError as exc:
                show_error(str(exc))
                press_any_key()
