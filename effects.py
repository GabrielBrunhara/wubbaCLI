"""Terminal animations and visual effects built on Rich."""
from __future__ import annotations

import os
import random
import sys
import time
from typing import Optional

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.text import Text

from settings import settings

console = Console()

# Characters used for the matrix rain
_MATRIX_CHARS = (
    "ﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "0123456789ABCDEF!@#$%^&*()[]"
    "∀∂∈ℝ∧∪≡∞↑↓←→"
)


# ── Primitives ────────────────────────────────────────────────────────────────

def _sleep(seconds: float) -> None:
    """Sleep only when effects are enabled."""
    if settings.effects_enabled:
        time.sleep(seconds)


def typing_effect(
    text: str,
    color: Optional[str] = None,
    delay: Optional[float] = None,
    end: str = "\n",
) -> None:
    """Print text one character at a time, typewriter-style."""
    c = color or settings.color_theme
    d = delay if delay is not None else settings.typing_speed
    if not settings.effects_enabled:
        console.print(f"[{c}]{text}[/{c}]", end=end)
        return
    for ch in text:
        sys.stdout.write(f"\033[38;2;{_hex_to_rgb(c)}m{ch}\033[0m")
        sys.stdout.flush()
        time.sleep(d)
    sys.stdout.write(end)
    sys.stdout.flush()


def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#rrggbb' to 'r;g;b' for ANSI escape."""
    h = hex_color.lstrip("#")
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r};{g};{b}"
    except (ValueError, IndexError):
        return "0;255;65"


# ── Boot screen ───────────────────────────────────────────────────────────────

SPLASH_ART = r"""
██████╗ ██╗ ██████╗██╗  ██╗    ████████╗███████╗██████╗ ███╗   ███╗
██╔══██╗██║██╔════╝██║ ██╔╝    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
██████╔╝██║██║     █████╔╝        ██║   █████╗  ██████╔╝██╔████╔██║
██╔══██╗██║██║     ██╔═██╗        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
██║  ██║██║╚██████╗██║  ██╗       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
"""

PORTAL_FRAMES = [
    "                         ·                         ",
    "                       (   )                       ",
    "                     (       )                     ",
    "                   ( ·  ░░░  · )                   ",
    "                 (   ░░░░░░░░░   )                 ",
    "               (   ░░░░░░░░░░░░░  )               ",
    "              (  ░░░░  PORTAL  ░░░░  )             ",
    "               (   ░░░░░░░░░░░░░  )               ",
    "                 (   ░░░░░░░░░   )                 ",
    "                   ( ·  ░░░  · )                   ",
    "                     (       )                     ",
    "                       (   )                       ",
]


def boot_screen() -> None:
    """Full boot sequence: banner → log lines → progress → ready."""
    os.system("cls" if os.name == "nt" else "clear")
    theme = settings.color_theme

    console.print(f"[bold {theme}]{SPLASH_ART}[/bold {theme}]", justify="center")
    console.print()

    boot_log = [
        ("Booting interdimensional database...",     theme),
        ("Calibrating Portal Gun oscillators...",    theme),
        ("Bypassing Galactic Federation firewall...", "yellow"),
        ("Decrypting Citadel of Ricks mainframe...", "cyan"),
        ("Loading Rick and Morty universe data...",  theme),
    ]
    for line, color in boot_log:
        typing_effect(f"  ▸ {line}", color, delay=0.012)
        _sleep(0.08)

    console.print()

    with Progress(
        SpinnerColumn(style=f"bold {theme}"),
        TextColumn(f"[bold {theme}]  Initializing Portal Gun"),
        BarColumn(bar_width=42, style=f"dim {theme}", complete_style=f"bold {theme}"),
        TextColumn(f"[bold {theme}]{{task.percentage:>3.0f}}%"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("boot", total=100)
        for _ in range(100):
            time.sleep(0.022)
            progress.advance(task)

    console.print()
    console.print(
        Align.center(
            Panel(
                f"[bold {theme}]  ✓  Connected to Dimension C-137  [/bold {theme}]",
                border_style=theme,
                padding=(0, 4),
            )
        )
    )
    _sleep(1.0)


# ── Matrix rain ───────────────────────────────────────────────────────────────

def matrix_rain(duration: Optional[float] = None) -> None:
    """Full-terminal matrix digital rain effect."""
    import shutil
    dur = duration if duration is not None else settings.matrix_duration
    cols, rows = shutil.get_terminal_size()
    theme = settings.color_theme

    # Each column tracks its current 'head' position
    heads = [random.randint(-(rows), rows) for _ in range(cols)]
    trail_len = 8

    with Live(refresh_per_second=24, screen=True) as live:
        deadline = time.time() + dur
        while time.time() < deadline:
            screen_lines: list[Text] = []
            for row in range(rows - 1):
                line = Text()
                for col in range(cols):
                    h = heads[col] % rows
                    dist = (row - h) % rows
                    if dist == 0:
                        line.append(random.choice(_MATRIX_CHARS), style="bold white")
                    elif dist <= trail_len:
                        alpha = 1.0 - dist / trail_len
                        if alpha > 0.6:
                            line.append(random.choice(_MATRIX_CHARS), style=f"bold {theme}")
                        elif alpha > 0.2:
                            line.append(random.choice(_MATRIX_CHARS), style=theme)
                        else:
                            line.append(random.choice(_MATRIX_CHARS), style=f"dim {theme}")
                    else:
                        if random.random() < 0.01:
                            line.append(random.choice(_MATRIX_CHARS), style=f"dim {theme}")
                        else:
                            line.append(" ")
                screen_lines.append(line)

            live.update(Group(*screen_lines))

            for i in range(cols):
                heads[i] += random.randint(0, 2)

            time.sleep(0.042)


# ── ASCII reveal ──────────────────────────────────────────────────────────────

def reveal_ascii_art(
    ascii_art: str,
    color: Optional[str] = None,
    delay: float = 0.012,
) -> None:
    """Reveal ASCII art line by line with a scanline effect."""
    c = color or settings.color_theme
    for line in ascii_art.split("\n"):
        console.print(f"[{c}]{line}[/{c}]")
        if settings.effects_enabled:
            time.sleep(delay)


# ── Portal transition ─────────────────────────────────────────────────────────

def portal_transition() -> None:
    """Animate a swirling portal opening then close it."""
    if not settings.effects_enabled:
        return
    theme = settings.color_theme
    for frame in PORTAL_FRAMES:
        console.print(f"[bold {theme}]{frame}[/bold {theme}]", justify="center")
        time.sleep(0.07)
    for frame in reversed(PORTAL_FRAMES[:-3]):
        console.print(f"[bold {theme}]{frame}[/bold {theme}]", justify="center")
        time.sleep(0.06)
    console.clear()


# ── Easter egg visuals ────────────────────────────────────────────────────────

PICKLE_RICK_ART = r"""
         ___
        /   \
       | o o |   I turned myself into a PICKLE!
        \___/    I'M PICKLE RIIIICK!!!
       /|   |\
      / |   | \
     /  |   |  \
    /   |___|   \
"""

WUBBA_LUBBA_ART = r"""
 __        __   _       _       _
 \ \      / /  | |__   | |__   | |  __ _
  \ \ /\ / /   | '_ \  | '_ \  | | / _` |
   \ V  V /    | |_) | | |_) | | || (_| |
    \_/\_/     |_.__/  |_.__/  |_| \__,_|

  _           _       _             _
 | |   _   _ | |__   | |__    __ _ | |
 | |  | | | || '_ \  | '_ \  / _` || |
 | |__| |_| || |_) | | |_) || (_| ||_|
 |_____\__,_||_.__/  |_.__/  \__,_|(_)

  ____              _       _
 |  _ \  _   _  _ | |     | |
 | | | || | | || |_| |     | |
 | |_| || |_| ||  _  |  _  |_|
 |____/  \__,_||_| |_| (_) (_)
"""

SECRET_PORTAL_ART = r"""
        ████████████████████████████
      ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
    ██░░░░   S E C R E T   M O D E  ░░░░██
   ██░░░░  ┌─────────────────────┐  ░░░░██
  ██░░░░   │  You found it.      │   ░░░░██
  ██░░░░   │  Wubba lubba        │   ░░░░██
  ██░░░░   │  dub dub, Morty!    │   ░░░░██
  ██░░░░   └─────────────────────┘   ░░░░██
   ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
      ████████████████████████████████
"""


def show_pickle_rick() -> None:
    theme = settings.color_theme
    console.print(
        Panel(
            f"[bold green]{PICKLE_RICK_ART}[/bold green]",
            title="[bold yellow]🥒  SECRET ACTIVATED  🥒[/bold yellow]",
            border_style=theme,
        ),
        justify="center",
    )
    _sleep(0.5)
    typing_effect("  > Morty, I turned myself into a pickle!", "green", delay=0.03)
    typing_effect("  > I'M PICKLE RIIIICK!", "yellow", delay=0.05)
    _sleep(1.5)


def show_wubba_lubba() -> None:
    theme = settings.color_theme
    console.print(
        Panel(
            f"[bold {theme}]{WUBBA_LUBBA_ART}[/bold {theme}]",
            title=f"[bold yellow]IT MEANS I AM IN GREAT PAIN[/bold yellow]",
            border_style=theme,
        ),
        justify="center",
    )
    _sleep(0.5)
    typing_effect("  > In Bird Culture, this is considered a big deal.", "cyan", delay=0.025)
    _sleep(1.5)


def show_portal_secret() -> None:
    theme = settings.color_theme
    os.system("cls" if os.name == "nt" else "clear")
    matrix_rain(duration=2.0)
    console.print(
        Panel(
            f"[bold {theme}]{SECRET_PORTAL_ART}[/bold {theme}]",
            title="[bold yellow]  ⌘  PORTAL GUN ACTIVATED  ⌘  [/bold yellow]",
            border_style=theme,
        ),
        justify="center",
    )
    _sleep(0.4)
    typing_effect("  > Sanchez-3000 interdimensional terminal unlocked.", theme, delay=0.02)
    typing_effect("  > Nice one, genius.", "cyan", delay=0.02)
    _sleep(2.0)


def show_get_schwifty() -> None:
    art = r"""
  ██████╗ ███████╗████████╗    ███████╗ ██████╗██╗  ██╗██╗    ██╗██╗███████╗████████╗██╗   ██╗
 ██╔════╝ ██╔════╝╚══██╔══╝    ██╔════╝██╔════╝██║  ██║██║    ██║██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
 ██║  ███╗█████╗     ██║       ███████╗██║     ███████║██║ █╗ ██║██║█████╗     ██║    ╚████╔╝
 ██║   ██║██╔══╝     ██║       ╚════██║██║     ██╔══██║██║███╗██║██║██╔══╝     ██║     ╚██╔╝
 ╚██████╔╝███████╗   ██║       ███████║╚██████╗██║  ██║╚███╔███╔╝██║██║        ██║      ██║
  ╚═════╝ ╚══════╝   ╚═╝       ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝      ╚═╝
    """
    theme = settings.color_theme
    console.print(f"[bold {theme}]{art}[/bold {theme}]", justify="center")
    typing_effect("  > Take off your pants and your panties...", "yellow", delay=0.03)
    typing_effect("  > Shit on the floor...", "yellow", delay=0.03)
    typing_effect("  > Time to GET SCHWIFTY in here!", "bold yellow", delay=0.05)
    _sleep(2.0)


def show_szechuan_sauce() -> None:
    theme = settings.color_theme
    console.print(
        Panel(
            "[bold yellow]I want that Mulan McNugget Sauce, Morty!\n\n"
            "That's my series arc, Morty!\n"
            "If it takes nine seasons, I want my\n"
            "[bold red]SZECHUAN DIPPING SAUCE[/bold red][bold yellow], Morty!\n\n"
            "— Rick Sanchez, C-137",
            title="[bold red]SZECHUAN SAUCE[/bold red]",
            border_style=theme,
        ),
        justify="center",
    )
    _sleep(2.5)
