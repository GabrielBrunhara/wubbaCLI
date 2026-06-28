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

from api import Character, Episode
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

def show_character_stats(char: Character) -> None:
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

    # Episode list (first 20)
    if char.episodes:
        ep_t = Table(show_header=False, border_style=f"dim {color}", box=None)
        ep_t.add_column(style=f"dim {color}", no_wrap=True)
        ep_t.add_column(style="white")
        shown = char.episodes[:20]
        for ep_url in shown:
            ep_id = ep_url.rstrip("/").split("/")[-1]
            ep_t.add_row(f"  Ep. {ep_id}", ep_url)
        if len(char.episodes) > 20:
            ep_t.add_row("  …", f"and {len(char.episodes) - 20} more")
        console.print(
            Panel(ep_t, title=f"[dim {color}]Episodes[/dim {color}]", border_style=f"dim {color}")
        )
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


# ── Press any key ─────────────────────────────────────────────────────────────

def press_any_key(msg: str = "Press Enter to continue...") -> None:
    color = _theme()
    try:
        input(f"\n  [{color}]{msg}[/{color}] ")
    except (EOFError, KeyboardInterrupt):
        pass
