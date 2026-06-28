"""All Rich-based display functions — the visual layer of the application."""
from __future__ import annotations

import sys
from typing import Callable, List, Optional, Set, Tuple

import readchar as _rc
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from api import Character, Episode, Location
from settings import settings

console = Console()

# ── Opacity cycle for ASCII art ───────────────────────────────────────────────
OPACITY_CYCLE = ["dim", "bold"]
OPACITY_LABEL = {"dim": "50%", "bold": "100%"}
OPACITY_STYLE = {
    "dim":    lambda c: f"dim {c}",
    "normal": lambda c: c,
    "bold":   lambda c: f"bold {c}",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _theme() -> str:
    return settings.color_theme


def _divider(title: str = "") -> None:
    console.print(Rule(title, style=_theme()))


def _info_table(rows: List[Tuple[str, str]], color: str) -> Table:
    t = Table.grid(padding=(0, 2))
    t.add_column(style=f"bold {color}", no_wrap=True)
    t.add_column()
    for label, value in rows:
        t.add_row(label, value)
    return t


# ── Single-keypress input ─────────────────────────────────────────────────────

def getch(valid: Set[str]) -> str:
    """Read one keypress without Enter. Falls back to line input in non-TTY."""
    if not sys.stdin.isatty():
        try:
            line = input().strip().upper()
        except (EOFError, OSError):
            raise KeyboardInterrupt
        ch = line[0] if line else ""
        return ch if ch in valid else (next(iter(sorted(valid)), "Q"))
    while True:
        try:
            raw = _rc.readchar()
        except Exception:
            raise KeyboardInterrupt
        if raw in ("\x03", "\x04"):
            raise KeyboardInterrupt
        key = raw.upper()
        if key in valid:
            color = _theme()
            console.print(f"[bold {color}]{key}[/bold {color}]")
            return key


def ask_play_again() -> bool:
    """Single-key Y/N prompt for 'play again?' in games."""
    color = _theme()
    console.print(f"\n  [bold {color}]Play again?[/bold {color}] [dim](y/n)[/dim] ", end="")
    console.file.flush()
    return getch({"Y", "N", "S"}) in ("Y", "S")


# ── Error / status messages ───────────────────────────────────────────────────

def show_error(message: str) -> None:
    console.print(
        Panel(f"[bold red]✖  {message}[/bold red]", border_style="red", padding=(0, 2))
    )


def show_success(message: str) -> None:
    color = _theme()
    console.print(
        Panel(f"[bold {color}]✓  {message}[/bold {color}]", border_style=color, padding=(0, 2))
    )


def show_info(message: str) -> None:
    console.print(f"[dim cyan]  ℹ  {message}[/dim cyan]")


def confirm(prompt: str) -> bool:
    color = _theme()
    console.print(f"[bold yellow]{prompt}[/bold yellow] [dim {color}](y/n)[/dim {color}] ", end="")
    console.file.flush()
    return getch({"Y", "N", "S"}) in ("Y", "S")


# ── Main menu ─────────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("C", "Character",        "Browse any character with full details"),
    ("B", "Search",           "Find a character by name"),
    # ("R", "Random",           "Random character — quick ASCII reveal"),
    ("E", "Episode",          "Explore a random episode of the show"),
    ("M", "Matrix Reveal",    "ASCII art emerges from the matrix rain"),
    ("G", "Games",            "Mini-games and trivia"),
    ("F", "Favorites",        "Your bookmarked characters"),
    ("H", "History",          "Recently viewed characters"),
    ("X", "Explore",          "Discover locations, dimensions & universe stats"),
    ("S", "Settings",         "Configure appearance and behavior"),
    ("Q", "Quit",             "Wubba lubba dub dub"),
]

GAMES_MENU_ITEMS = [
    ("G", "Guess Who",        "Identify the character from their ASCII art"),
    ("A", "Alive or Dead",    "Is this character still breathing?"),
    ("S", "Species Roulette", "Guess the species of a random character"),
    ("E", "Episode Counter",  "How many episodes did they appear in?"),
    ("R", "Random Game",      "Let the universe decide"),
    ("P", "Scores",           "View your game scores"),
    ("Q", "Back",             ""),
]


def show_menu() -> str:
    """Render the main menu and return the user's choice (uppercased)."""
    color = _theme()
    console.print()

    from effects import get_title_art
    from rich.text import Text as _Text
    console.print(_Text(get_title_art(), style=f"bold {color}"), justify="center")

    # Build the menu table
    t = Table.grid(padding=(0, 3))
    t.add_column(style=f"bold {color}", width=4, justify="right")
    t.add_column(style="bold white", width=20)
    t.add_column(style="dim white")

    for key, name, desc in MENU_ITEMS:
        t.add_row(f"[{color}]{key}[/{color}]", name, desc)

    console.print(
        Panel(
            Align.center(t),
            title=f"[bold {color}]   MAIN MENU   [/bold {color}]",
            subtitle=f"[dim {color}]Type a letter and press Enter[/dim {color}]",
            border_style=color,
            padding=(1, 4),
        )
    )
    console.print()

    valid = {item[0] for item in MENU_ITEMS}
    console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
    console.file.flush()
    return getch(valid)


def show_games_menu() -> str:
    """Render the games submenu and return the user's choice."""
    color = _theme()
    console.print()

    t = Table.grid(padding=(0, 3))
    t.add_column(style=f"bold {color}", width=4, justify="right")
    t.add_column(style="bold white", width=20)
    t.add_column(style="dim white")

    for key, name, desc in GAMES_MENU_ITEMS:
        t.add_row(f"[{color}]{key}[/{color}]", name, desc)

    console.print(
        Panel(
            Align.center(t),
            title=f"[bold {color}]  GAMES & TRIVIA  [/bold {color}]",
            border_style=color,
            padding=(1, 4),
        )
    )
    console.print()

    valid = {item[0] for item in GAMES_MENU_ITEMS}
    console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
    console.file.flush()
    return getch(valid)


def show_game_screen(
    art: str,
    title: str,
    subtitle: str,
    info_rows: List[Tuple[str, str]],
    options: List[str],
    prompt: str = "Your answer",
) -> int:
    """ASCII art (left) + game info and choices (right). Returns 0-based chosen index."""
    color = _theme()
    letters = "ABCD"

    ascii_text = Text(art, style=f"bold {color}", overflow="fold", no_wrap=True)
    ascii_panel = Panel(ascii_text, border_style=color, padding=(0, 1))

    info_t = _info_table(info_rows, color)

    opts_t = Table.grid(padding=(0, 2))
    opts_t.add_column(style=f"bold {color}", width=4, justify="right")
    opts_t.add_column(style="bold white")
    for i, opt in enumerate(options):
        opts_t.add_row(f"[{color}]{letters[i]}[/{color}]", opt)

    right_panel = Panel(
        Group(info_t, Text(""), opts_t),
        title=f"[bold {color}]{title}[/bold {color}]",
        subtitle=f"[dim {color}]{subtitle}[/dim {color}]",
        border_style=color,
        padding=(1, 2),
    )

    console.print()
    console.print(Columns([ascii_panel, right_panel], equal=False, expand=True))
    console.print()

    valid = set(letters[: len(options)])
    console.print(f"  [bold {color}]{prompt}[/bold {color}] ", end="")
    console.file.flush()
    return letters.index(getch(valid))


# ── Character display ─────────────────────────────────────────────────────────

def show_character(
    char: Character,
    ascii_art: str,
    is_favorite: bool = False,
    opacity: str = "dim",
) -> None:
    """Main character view: ASCII art left, info panel right."""
    color = _theme()
    console.print()
    _divider(f"  #{char.id}  {char.name}  ")

    # Status pill
    status_style = char.status_color
    status_text = f"[bold {status_style}]{char.status_icon} {char.status}[/bold {status_style}]"

    fav_badge = f"[bold yellow] ★ FAVORITE[/bold yellow]" if is_favorite else ""

    # Info panel content
    info_rows: List[Tuple[str, str]] = [
        ("ID",        str(char.id)),
        ("Status",    char.status),
        ("Species",   char.species or "Unknown"),
        ("Type",      char.type or "—"),
        ("Gender",    char.gender),
        ("Origin",    char.origin),
        ("Location",  char.location),
        ("Episodes",  str(char.episode_count)),
    ]
    info_table = _info_table(info_rows, color)

    info_panel = Panel(
        info_table,
        title=f"[bold {color}]{char.name}[/bold {color}] {fav_badge}",
        subtitle=status_text,
        border_style=color,
        padding=(1, 2),
    )

    # ASCII panel — brightness controlled by opacity param
    ascii_style = OPACITY_STYLE.get(opacity, OPACITY_STYLE["dim"])(color)
    ascii_text = Text(ascii_art, style=ascii_style, overflow="fold", no_wrap=True)
    pct = OPACITY_LABEL.get(opacity, "50%")
    ascii_panel = Panel(
        ascii_text,
        title=f"[dim {color}]ASCII  ·  {settings.charset_name}[/dim {color}]",
        border_style=color,
        padding=(0, 1),
    )

    cols = Columns([ascii_panel, info_panel], equal=False, expand=True)
    console.print(cols)

    # Controls hint
    console.print()
    console.print(
        f"  [dim]"
        f"[{color}]F[/{color}] Favorite  "
        f"[{color}]E[/{color}] Export  "
        f"[{color}]S[/{color}] Stats  "
        f"[{color}]T[/{color}] Opacity [{color}]{pct}[/{color}]  "
        f"[{color}]Q[/{color}] Back"
        f"[/dim]"
    )
    console.print()


def show_character_action_prompt() -> str:
    color = _theme()
    console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
    console.file.flush()
    return getch({"F", "E", "S", "T", "Q", "B"})


# ── Episode display ───────────────────────────────────────────────────────────

def show_episode(episode: Episode, characters: List[Character]) -> None:
    color = _theme()
    console.print()
    _divider(f"  {episode.episode} — {episode.name}  ")

    meta_rows: List[Tuple[str, str]] = [
        ("Code",        episode.episode),
        ("Air Date",    episode.air_date),
        ("Characters",  str(episode.character_count)),
    ]
    meta_table = _info_table(meta_rows, color)
    console.print(
        Panel(
            meta_table,
            title=f"[bold {color}]{episode.name}[/bold {color}]",
            border_style=color,
            padding=(1, 2),
        )
    )

    if characters:
        console.print()
        console.print(f"  [bold {color}]Characters in this episode:[/bold {color}]")
        console.print()
        t = Table(
            show_header=True,
            header_style=f"bold {color}",
            border_style=f"dim {color}",
        )
        t.add_column("#", style="dim", width=4)
        t.add_column("Name", style="bold white")
        t.add_column("Status", style="bold")
        t.add_column("Species")
        for i, c in enumerate(characters, 1):
            t.add_row(
                str(i),
                c.name,
                f"[{c.status_color}]{c.status_icon} {c.status}[/{c.status_color}]",
                c.species,
            )
        console.print(t)

    console.print()
    console.print(
        f"  [dim][{color}]<number>[/{color}] Open character  [{color}]Q[/{color}] Back[/dim]"
    )
    console.print()


# ── Search results ────────────────────────────────────────────────────────────

def show_search_results(characters: List[Character]) -> Optional[int]:
    """Show numbered list; return selected index or None (Q to cancel)."""
    if not characters:
        show_error("No characters found.")
        return None

    color = _theme()
    console.print()

    t = Table(
        show_header=True,
        header_style=f"bold {color}",
        border_style=f"dim {color}",
    )
    t.add_column("#", style="dim", width=5, justify="right")
    t.add_column("Name", style="bold white")
    t.add_column("Status")
    t.add_column("Species")
    t.add_column("Episodes", justify="right")

    for i, c in enumerate(characters, 1):
        t.add_row(
            str(i),
            c.name,
            f"[{c.status_color}]{c.status_icon} {c.status}[/{c.status_color}]",
            c.species,
            str(c.episode_count),
        )

    console.print(
        Panel(
            t,
            title=f"[bold {color}]  Search Results — {len(characters)} found  [/bold {color}]",
            border_style=color,
        )
    )
    console.print()
    raw = Prompt.ask(
        f"  [bold {color}]Enter number to open (or Q to cancel)[/bold {color}]"
    ).strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(characters):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


# ── Favorites / History list ──────────────────────────────────────────────────

def show_character_list(characters: List[Character], title: str) -> Optional[int]:
    """Generic numbered list picker. Returns 0-based index or None."""
    if not characters:
        show_info("The list is empty.")
        return None

    color = _theme()
    console.print()

    t = Table(
        show_header=True,
        header_style=f"bold {color}",
        border_style=f"dim {color}",
    )
    t.add_column("#", style="dim", width=5, justify="right")
    t.add_column("Name", style="bold white")
    t.add_column("Status")
    t.add_column("Species")
    t.add_column("Episodes", justify="right")

    for i, c in enumerate(characters, 1):
        t.add_row(
            str(i),
            c.name,
            f"[{c.status_color}]{c.status_icon} {c.status}[/{c.status_color}]",
            c.species,
            str(c.episode_count),
        )

    console.print(
        Panel(t, title=f"[bold {color}]  {title}  [/bold {color}]", border_style=color)
    )
    console.print()
    raw = Prompt.ask(
        f"  [bold {color}]Enter number to open (or Q to cancel)[/bold {color}]"
    ).strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(characters):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


# ── Stats panel ───────────────────────────────────────────────────────────────

def show_character_stats(char: Character, all_episodes=None) -> None:
    color = _theme()
    console.print()
    _divider(f"  Character Stats — {char.name}  ")

    rows: List[Tuple[str, str]] = [
        ("ID",            str(char.id)),
        ("Full Name",     char.name),
        ("Status",        f"{char.status_icon} {char.status}"),
        ("Species",       char.species or "Unknown"),
        ("Subspecies",    char.type or "—"),
        ("Gender",        char.gender),
        ("Origin",        char.origin),
        ("Last Location", char.location),
        ("Episode Count", str(char.episode_count)),
        ("API URL",       char.url),
        ("Created",       char.created[:10]),
        ("Image URL",     char.image),
    ]

    t = _info_table(rows, color)
    console.print(
        Panel(t, title=f"[bold {color}]{char.name}[/bold {color}]", border_style=color, padding=(1, 4))
    )

    if all_episodes:
        show_character_timeline(char, all_episodes)
    else:
        console.print()


# ── Settings menu ─────────────────────────────────────────────────────────────

def show_settings(current: "settings") -> str:
    """Display settings panel and return selected key or Q."""
    from settings import CHARSETS, THEMES, FIGLET_FONTS
    color = _theme()
    console.print()
    _divider("  Settings  ")

    options = [
        ("W", "ASCII Width",      str(current.width)),
        ("A", "Auto Width",       "ON" if current.auto_width else "OFF"),
        ("C", "Charset",          current.charset_name),
        ("T", "Color Theme",      current.color_theme_name),
        ("F", "Figlet Font",      current.figlet_font),
        ("E", "Effects",          "ON" if current.effects_enabled else "OFF"),
        ("B", "Boot Style",       current.boot_style.capitalize()),
        ("S", "Typing Speed",     str(current.typing_speed)),
        ("R", "Reset Defaults",   ""),
        ("X", "Clear Cache",      ""),
        ("Q", "Back",             ""),
    ]

    t = Table.grid(padding=(0, 3))
    t.add_column(style=f"bold {color}", width=4, justify="right")
    t.add_column(style="bold white", width=20)
    t.add_column(style=color)

    for key, label, val in options:
        t.add_row(f"[{color}]{key}[/{color}]", label, val)

    console.print(
        Panel(
            Align.center(t),
            title=f"[bold {color}]  Settings  [/bold {color}]",
            border_style=color,
            padding=(1, 4),
        )
    )
    console.print()
    console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
    console.file.flush()
    return getch({"W", "A", "C", "T", "F", "E", "B", "S", "R", "X", "Q"})


# ── Export prompt ─────────────────────────────────────────────────────────────

def show_export_menu() -> str:
    color = _theme()
    t = Table.grid(padding=(0, 3))
    t.add_column(style=f"bold {color}", width=4)
    t.add_column(style="bold white")
    t.add_row("T", "Export as TXT")
    t.add_row("H", "Export as HTML")
    t.add_row("Q", "Back")
    console.print(
        Panel(
            Align.center(t),
            title=f"[bold {color}]  Export ASCII Art  [/bold {color}]",
            border_style=color,
            padding=(1, 3),
        )
    )
    console.print()
    console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
    console.file.flush()
    return getch({"T", "H", "Q"})


# ── Game UI helpers ───────────────────────────────────────────────────────────

def show_game_header(title: str, subtitle: str = "") -> None:
    color = _theme()
    console.print()
    console.print(
        Panel(
            f"[bold white]{subtitle}[/bold white]" if subtitle else "",
            title=f"[bold {color}]  {title}  [/bold {color}]",
            border_style=color,
            padding=(0, 4),
        )
    )
    console.print()


def show_multiple_choice(options: List[str], prompt: str = "Your answer") -> int:
    """Show A/B/C/D choices; return 0-based index of selection."""
    color = _theme()
    letters = "ABCDEFGHIJ"
    t = Table.grid(padding=(0, 3))
    t.add_column(style=f"bold {color}", width=4)
    t.add_column(style="bold white")
    for i, opt in enumerate(options):
        t.add_row(f"[{color}]{letters[i]}[/{color}]", opt)
    console.print(t)
    console.print()

    valid = set(letters[: len(options)])
    console.print(f"  [bold {color}]{prompt}[/bold {color}] ", end="")
    console.file.flush()
    key = getch(valid)
    return letters.index(key)


def show_game_result(correct: bool, correct_answer: str, score: int, total: int) -> None:
    color = _theme()
    if correct:
        console.print(
            Panel(
                f"[bold green]✓ CORRECT![/bold green]\n[dim white]{correct_answer}[/dim white]",
                border_style="green",
                padding=(0, 3),
            )
        )
    else:
        console.print(
            Panel(
                f"[bold red]✖ WRONG![/bold red]\n"
                f"[dim white]The answer was: [bold white]{correct_answer}[/bold white][/dim white]",
                border_style="red",
                padding=(0, 3),
            )
        )
    console.print(
        f"  [dim]Score: [bold {color}]{score}[/bold {color}] / {total}[/dim]"
    )
    console.print()


def show_score_board(scores: dict) -> None:
    color = _theme()
    console.print()
    t = Table(
        show_header=True,
        header_style=f"bold {color}",
        border_style=f"dim {color}",
    )
    t.add_column("Game", style="bold white")
    t.add_column("Wins", justify="right", style="green")
    t.add_column("Losses", justify="right", style="red")
    t.add_column("Win%", justify="right", style=color)

    for game, data in scores.items():
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        total = wins + losses
        pct = f"{wins / total * 100:.0f}%" if total else "—"
        t.add_row(game, str(wins), str(losses), pct)

    console.print(
        Panel(t, title=f"[bold {color}]  Score Board  [/bold {color}]", border_style=color)
    )
    console.print()


# ── Explore submenu ───────────────────────────────────────────────────────────

EXPLORE_MENU_ITEMS = [
    ("L", "Locations",       "Browse all 126 known locations"),
    ("D", "Dimensions",      "Atlas of every discovered dimension"),
    ("N", "Universe Census", "Live stats across all 826 characters"),
    ("S", "Season Guide",    "All episodes organised by season"),
    ("W", "Most Wanted",     "Leaderboards across the universe"),
    ("K", "Dead Roster",     "Log of all confirmed casualties"),
    ("Q", "Back",            ""),
]


def show_explore_menu() -> str:
    color = _theme()
    console.print()
    t = Table.grid(padding=(0, 3))
    t.add_column(style=f"bold {color}", width=4, justify="right")
    t.add_column(style="bold white", width=22)
    t.add_column(style="dim white")
    for key, name, desc in EXPLORE_MENU_ITEMS:
        t.add_row(f"[{color}]{key}[/{color}]", name, desc)
    console.print(Panel(
        Align.center(t),
        title=f"[bold {color}]  EXPLORE THE UNIVERSE  [/bold {color}]",
        border_style=color, padding=(1, 4),
    ))
    console.print()
    valid = {item[0] for item in EXPLORE_MENU_ITEMS}
    console.print(f"  [bold {color}]▶[/bold {color}] ", end="")
    console.file.flush()
    return getch(valid)


# ── Location display ───────────────────────────────────────────────────────────

def show_location_list(locations: List[Location], title: str) -> Optional[int]:
    if not locations:
        show_info("No locations found.")
        return None
    color = _theme()
    console.print()
    t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    t.add_column("#", style="dim", width=5, justify="right")
    t.add_column("Name", style="bold white")
    t.add_column("Type")
    t.add_column("Dimension")
    t.add_column("Residents", justify="right", style=color)
    for i, loc in enumerate(locations, 1):
        t.add_row(str(i), loc.name, loc.type, loc.dimension, str(loc.resident_count))
    console.print(Panel(t, title=f"[bold {color}]  {title}  [/bold {color}]", border_style=color))
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Enter number to open (or Q)[/bold {color}]").strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(locations):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


def show_location(location: Location, residents: List[Character]) -> None:
    color = _theme()
    console.print()
    _divider(f"  #{location.id}  {location.name}  ")
    rows: List[Tuple[str, str]] = [
        ("Type",      location.type),
        ("Dimension", location.dimension),
        ("Residents", str(location.resident_count)),
    ]
    console.print(Panel(
        _info_table(rows, color),
        title=f"[bold {color}]{location.name}[/bold {color}]",
        border_style=color, padding=(1, 2),
    ))
    if residents:
        console.print()
        t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
        t.add_column("#", style="dim", width=4)
        t.add_column("Name", style="bold white")
        t.add_column("Status")
        t.add_column("Species")
        for i, c in enumerate(residents, 1):
            t.add_row(
                str(i), c.name,
                f"[{c.status_color}]{c.status_icon} {c.status}[/{c.status_color}]",
                c.species,
            )
        console.print(t)
    console.print()
    console.print(f"  [dim][{color}]<number>[/{color}] Open resident  [{color}]Q[/{color}] Back[/dim]")
    console.print()


# ── Dimension atlas ────────────────────────────────────────────────────────────

def show_dimension_list(dims: List[Tuple[str, int, int]]) -> Optional[int]:
    """dims: list of (dimension_name, location_count, resident_count). Returns index or None."""
    color = _theme()
    console.print()
    t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    t.add_column("#", style="dim", width=5, justify="right")
    t.add_column("Dimension", style="bold white")
    t.add_column("Locations", justify="right", style=color)
    t.add_column("Residents", justify="right")
    for i, (name, locs, res) in enumerate(dims, 1):
        t.add_row(str(i), name, str(locs), str(res))
    console.print(Panel(
        t,
        title=f"[bold {color}]  DIMENSION ATLAS — {len(dims)} dimensions  [/bold {color}]",
        border_style=color,
    ))
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Enter number to explore (or Q)[/bold {color}]").strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(dims):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


# ── Census ─────────────────────────────────────────────────────────────────────

def _bar(count: int, total: int, width: int = 28) -> str:
    filled = round(count / total * width) if total else 0
    return f"[green]{'█' * filled}[/green][dim]{'░' * (width - filled)}[/dim]"


def show_census(stats: dict) -> None:
    color = _theme()
    console.print()
    _divider("  Universe Census  ")

    # Totals header
    totals = Table.grid(padding=(0, 4))
    totals.add_column(justify="center", style=f"bold {color}")
    totals.add_column(justify="center", style=f"bold {color}")
    totals.add_column(justify="center", style=f"bold {color}")
    totals.add_row(
        f"[bold white]{stats['total_chars']}[/bold white]\ncharacters",
        f"[bold white]{stats['total_locs']}[/bold white]\nlocations",
        f"[bold white]{stats['total_eps']}[/bold white]\nepisodes",
    )
    console.print(Panel(Align.center(totals), border_style=color, padding=(0, 4)))
    console.print()

    # Status breakdown
    total = stats["total_chars"]
    status_t = Table.grid(padding=(0, 2))
    status_t.add_column(width=10, style="bold white")
    status_t.add_column(width=30)
    status_t.add_column(width=8, justify="right", style=color)
    status_t.add_column(width=6, justify="right", style="dim")
    for label, key, col in [("Alive", "alive", "green"), ("Dead", "dead", "red"), ("Unknown", "unknown", "yellow")]:
        n = stats[key]
        pct = f"{n/total*100:.0f}%"
        status_t.add_row(label, _bar(n, total), str(n), pct)
    console.print(Panel(status_t, title=f"[bold {color}]Status[/bold {color}]", border_style=f"dim {color}", padding=(1, 2)))
    console.print()

    # Species top 10
    species_t = Table.grid(padding=(0, 2))
    species_t.add_column(width=22, style="bold white")
    species_t.add_column(width=30)
    species_t.add_column(width=6, justify="right", style=color)
    top_sp = stats["species"][:10]
    max_sp = top_sp[0][1] if top_sp else 1
    for sp, n in top_sp:
        species_t.add_row(sp, _bar(n, max_sp), str(n))
    console.print(Panel(species_t, title=f"[bold {color}]Top Species[/bold {color}]", border_style=f"dim {color}", padding=(1, 2)))
    console.print()

    # Gender breakdown
    gender_t = Table.grid(padding=(0, 2))
    gender_t.add_column(width=12, style="bold white")
    gender_t.add_column(width=30)
    gender_t.add_column(width=6, justify="right", style=color)
    for g, n in stats["gender"].items():
        gender_t.add_row(g.title(), _bar(n, total), str(n))
    console.print(Panel(gender_t, title=f"[bold {color}]Gender[/bold {color}]", border_style=f"dim {color}", padding=(1, 2)))
    console.print()

    # Top locations
    loc_t = Table.grid(padding=(0, 2))
    loc_t.add_column(width=30, style="bold white")
    loc_t.add_column(width=30)
    loc_t.add_column(width=6, justify="right", style=color)
    top_locs = stats["locations"][:8]
    max_loc = top_locs[0][1] if top_locs else 1
    for loc, n in top_locs:
        loc_t.add_row(loc, _bar(n, max_loc), str(n))
    console.print(Panel(loc_t, title=f"[bold {color}]Most Populated Locations[/bold {color}]", border_style=f"dim {color}", padding=(1, 2)))
    console.print()


# ── Season guide ───────────────────────────────────────────────────────────────

def show_season_list(seasons: List[Tuple[str, List["Episode"]]]) -> Optional[int]:
    """Show season summary; return 0-based season index or None."""
    color = _theme()
    console.print()
    t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    t.add_column("Season", style="bold white", width=8)
    t.add_column("Episodes", justify="right", style=color)
    t.add_column("Characters", justify="right")
    t.add_column("Air Window")
    for label, eps in seasons:
        chars = sum(e.character_count for e in eps)
        air = f"{eps[0].air_date}  →  {eps[-1].air_date}" if eps else ""
        t.add_row(label, str(len(eps)), str(chars), air)
    console.print(Panel(t, title=f"[bold {color}]  Episode Guide  [/bold {color}]", border_style=color))
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Enter season number (1-5) or Q[/bold {color}]").strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(seasons):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


def show_season_episodes(label: str, episodes: List["Episode"]) -> Optional[int]:
    color = _theme()
    console.print()
    t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    t.add_column("#", style="dim", width=4)
    t.add_column("Code", style=color, width=8)
    t.add_column("Title", style="bold white")
    t.add_column("Air Date")
    t.add_column("Cast", justify="right")
    for i, ep in enumerate(episodes, 1):
        t.add_row(str(i), ep.episode, ep.name, ep.air_date, str(ep.character_count))
    console.print(Panel(t, title=f"[bold {color}]  {label}  [/bold {color}]", border_style=color))
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Enter episode number for Cast Roll (or Q)[/bold {color}]").strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(episodes):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


# ── Character timeline ─────────────────────────────────────────────────────────

def show_character_timeline(char: Character, all_episodes: List["Episode"]) -> None:
    color = _theme()
    appeared = {int(u.rstrip("/").split("/")[-1]) for u in char.episodes}
    seasons = [
        ("S1", range(1, 12)), ("S2", range(12, 22)), ("S3", range(22, 32)),
        ("S4", range(32, 42)), ("S5", range(42, 52)),
    ]
    ep_map = {e.id: e for e in all_episodes}
    console.print()
    _divider(f"  Episode Timeline — {char.name}  ")

    grid_t = Table.grid(padding=(0, 1))
    grid_t.add_column(width=4, style="dim")
    grid_t.add_column()
    for s_label, s_range in seasons:
        cells = Text()
        for n in s_range:
            if n in appeared:
                cells.append("■ ", style=f"bold {color}")
            else:
                cells.append("□ ", style="dim")
        grid_t.add_row(s_label, cells)

    ep_ids_sorted = sorted(appeared)
    first_ep = ep_map.get(ep_ids_sorted[0]) if ep_ids_sorted else None
    last_ep  = ep_map.get(ep_ids_sorted[-1]) if ep_ids_sorted else None

    footer_rows: List[Tuple[str, str]] = [
        ("Appearances", f"{char.episode_count} / 51"),
    ]
    if first_ep:
        footer_rows.append(("First seen", f"{first_ep.episode} — {first_ep.name}  ({first_ep.air_date})"))
    if last_ep and last_ep.id != (first_ep.id if first_ep else -1):
        footer_rows.append(("Last seen",  f"{last_ep.episode} — {last_ep.name}  ({last_ep.air_date})"))

    console.print(Panel(
        Group(grid_t, Text(""), _info_table(footer_rows, color)),
        title=f"[bold {color}]{char.name}[/bold {color}]",
        border_style=color, padding=(1, 2),
    ))
    console.print()


# ── Leaderboard ────────────────────────────────────────────────────────────────

def show_leaderboard(chars: List[Character]) -> None:
    color = _theme()
    console.print()
    _divider("  Most Wanted — Universe Leaderboard  ")

    # Most appearances
    top_chars = sorted(chars, key=lambda c: c.episode_count, reverse=True)[:10]
    app_t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    app_t.add_column("#", style="dim", width=4)
    app_t.add_column("Name", style="bold white")
    app_t.add_column("Episodes", justify="right", style=color)
    app_t.add_column("Status")
    app_t.add_column("Species")
    for i, c in enumerate(top_chars, 1):
        app_t.add_row(
            str(i), c.name, str(c.episode_count),
            f"[{c.status_color}]{c.status_icon} {c.status}[/{c.status_color}]", c.species,
        )
    console.print(Panel(app_t, title=f"[bold {color}]Most Appearances[/bold {color}]", border_style=f"dim {color}"))
    console.print()

    # Species distribution (top 8)
    from collections import Counter
    sp_count = Counter(c.species for c in chars)
    sp_t = Table.grid(padding=(0, 2))
    sp_t.add_column(width=24, style="bold white")
    sp_t.add_column(width=30)
    sp_t.add_column(width=6, justify="right", style=color)
    top_sp = sp_count.most_common(8)
    max_n = top_sp[0][1] if top_sp else 1
    for sp, n in top_sp:
        sp_t.add_row(sp, _bar(n, max_n), str(n))
    console.print(Panel(sp_t, title=f"[bold {color}]Species Distribution[/bold {color}]", border_style=f"dim {color}", padding=(1, 2)))
    console.print()

    # Deadliest species
    dead = [c for c in chars if c.status.lower() == "dead"]
    dead_sp = Counter(c.species for c in dead)
    dead_t = Table.grid(padding=(0, 2))
    dead_t.add_column(width=24, style="bold white")
    dead_t.add_column(width=30)
    dead_t.add_column(width=6, justify="right", style="red")
    top_dead = dead_sp.most_common(8)
    max_d = top_dead[0][1] if top_dead else 1
    for sp, n in top_dead:
        dead_t.add_row(sp, _bar(n, max_d), str(n))
    console.print(Panel(dead_t, title=f"[bold {color}]Most Deaths by Species[/bold {color}]", border_style=f"dim {color}", padding=(1, 2)))
    console.print()


# ── Dead roster ────────────────────────────────────────────────────────────────

def show_dead_roster(chars: List[Character], page: int, per_page: int = 25) -> Optional[int]:
    color = _theme()
    total_pages = (len(chars) - 1) // per_page + 1
    start = page * per_page
    chunk = chars[start: start + per_page]
    console.print()
    t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    t.add_column("#", style="dim", width=5, justify="right")
    t.add_column("Name", style="bold white")
    t.add_column("Species")
    t.add_column("Last Known Location")
    for i, c in enumerate(chunk, start + 1):
        t.add_row(str(i), c.name, c.species, c.location)
    console.print(Panel(
        t,
        title=f"[bold red]  ✕ DEAD ROSTER — {len(chars)} casualties  [/bold red]",
        subtitle=f"[dim {color}]Page {page+1}/{total_pages}[/dim {color}]",
        border_style="red",
    ))
    console.print()
    console.print(
        f"  [dim][{color}]<number>[/{color}] Open  "
        f"[{color}]N[/{color}] Next  [{color}]P[/{color}] Prev  [{color}]Q[/{color}] Back[/dim]"
    )
    console.print()
    raw = Prompt.ask(f"  [bold {color}]▶[/bold {color}]").strip().upper()
    if raw == "Q":
        return None
    if raw == "N":
        return -(page + 1) - 1  # encode "next page" as negative
    if raw == "P":
        return -(page - 1) - 1  # encode "prev page" as negative
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(chars):
            return idx
    except ValueError:
        pass
    show_error("Invalid input.")
    return -999


def show_costar_results(costars: List[Tuple[Character, int]], target_name: str) -> Optional[int]:
    color = _theme()
    console.print()
    t = Table(show_header=True, header_style=f"bold {color}", border_style=f"dim {color}")
    t.add_column("#", style="dim", width=4)
    t.add_column("Name", style="bold white")
    t.add_column("Shared Eps", justify="right", style=color)
    t.add_column("Status")
    t.add_column("Species")
    for i, (c, shared) in enumerate(costars, 1):
        t.add_row(
            str(i), c.name, str(shared),
            f"[{c.status_color}]{c.status_icon} {c.status}[/{c.status_color}]",
            c.species,
        )
    console.print(Panel(
        t,
        title=f"[bold {color}]  Co-Stars of {target_name}  [/bold {color}]",
        border_style=color,
    ))
    console.print()
    raw = Prompt.ask(f"  [bold {color}]Enter number to open (or Q)[/bold {color}]").strip()
    if raw.upper() == "Q":
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(costars):
            return idx
    except ValueError:
        pass
    show_error("Invalid selection.")
    return None


# ── Press any key ─────────────────────────────────────────────────────────────

def press_any_key(msg: str = "Press Enter to continue...") -> None:
    color = _theme()
    try:
        console.input(f"\n  [{color}]{msg}[/{color}] ")
    except (EOFError, KeyboardInterrupt):
        pass
