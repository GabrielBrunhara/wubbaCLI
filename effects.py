"""Terminal animations and visual effects built on Rich."""
from __future__ import annotations

import math
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

APP_NAME = "WubbaCLI"

SPLASH_ART = r"""
██╗    ██╗██╗   ██╗██████╗ ██████╗  █████╗  ██████╗██╗     ██╗
██║    ██║██║   ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝██║     ██║
██║ █╗ ██║██║   ██║██████╔╝██████╔╝███████║██║     ██║     ██║
██║███╗██║██║   ██║██╔══██╗██╔══██╗██╔══██║██║     ██║     ██║
╚███╔███╔╝╚██████╔╝██████╔╝██████╔╝██║  ██║╚██████╗███████╗██║
 ╚══╝╚══╝  ╚═════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝
"""


def get_title_art() -> str:
    """Render APP_NAME with the current figlet font. Falls back to SPLASH_ART."""
    try:
        from pyfiglet import Figlet
        return Figlet(font=settings.figlet_font).renderText(APP_NAME)
    except Exception:
        return SPLASH_ART



def _boot_log_and_progress() -> None:
    """Boot log lines, progress bar, and ready panel (shared by both boot styles)."""
    theme = settings.color_theme
    boot_log = [
        ("Booting interdimensional database...",      theme),
        ("Calibrating Portal Gun oscillators...",     theme),
        ("Bypassing Galactic Federation firewall...", "yellow"),
        ("Decrypting Citadel of Ricks mainframe...",  "cyan"),
        ("Loading Rick and Morty universe data...",   theme),
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


def boot_screen() -> None:
    """Classic boot: banner → log lines → progress → ready."""
    os.system("cls" if os.name == "nt" else "clear")
    theme = settings.color_theme
    console.print(Text(get_title_art(), style=f"bold {theme}"), justify="center")
    console.print()
    _boot_log_and_progress()


def epic_boot_screen() -> None:
    """Portal boot: beam fires → portal opens → RICK TERMINAL materializes through it."""
    import shutil

    if not settings.effects_enabled:
        boot_screen()
        return

    os.system("cls" if os.name == "nt" else "clear")
    cols, rows = shutil.get_terminal_size()
    theme = settings.color_theme

    cx     = cols / 2.0
    cy     = rows / 2.0
    ASPECT = 0.45
    max_r  = min(rows * 0.40, cols * ASPECT * 0.42)

    # ── Beam: bottom-left corner → screen center ──────────────────────────────
    NOZZLE_R = rows - 2
    NOZZLE_C = 0
    TARGET_R = int(cy)
    TARGET_C = int(cx)

    beam_cells: list = []
    _seen: set = set()
    steps = max(abs(TARGET_C - NOZZLE_C), abs(TARGET_R - NOZZLE_R))
    for i in range(steps + 1):
        frac = i / steps if steps else 0.0
        br   = round(NOZZLE_R + frac * (TARGET_R - NOZZLE_R))
        bc   = round(NOZZLE_C + frac * (TARGET_C - NOZZLE_C))
        if (br, bc) not in _seen:
            beam_cells.append((br, bc))
            _seen.add((br, bc))

    beam_pos: dict = {pos: i for i, pos in enumerate(beam_cells)}

    # ── Logo layout: current figlet font, centered, chars sorted by distance ────
    logo_lines = get_title_art().strip("\n").split("\n")
    logo_h = len(logo_lines)
    logo_w = max(len(l) for l in logo_lines)
    logo_r0 = int(cy) - logo_h // 2
    logo_c0 = int(cx) - logo_w // 2

    def _vdist(r: int, c: int) -> float:
        return math.sqrt(((c - cx) * ASPECT) ** 2 + (r - cy) ** 2)

    art_chars: dict = {}
    for r_off, ll in enumerate(logo_lines):
        for c_off, ch in enumerate(ll):
            if ch.strip():
                art_chars[(logo_r0 + r_off, logo_c0 + c_off)] = ch

    art_sorted: list = sorted(art_chars.keys(), key=lambda p: _vdist(p[0], p[1]))
    revealed:   set  = set()

    # ── Phase timing ──────────────────────────────────────────────────────────
    SHOT_DUR   = 0.8
    OPEN_DUR   = 1.4
    SPIN_DUR   = 1.5
    REVEAL_DUR = 1.2
    HOLD_DUR   = 0.4
    CLOSE_DUR  = 0.7

    T_OPEN   = SHOT_DUR               # 0.8  portal opens as beam arrives
    T_SPIN   = T_OPEN   + OPEN_DUR    # 2.2
    T_REVEAL = T_SPIN   + SPIN_DUR    # 3.7
    T_HOLD   = T_REVEAL + REVEAL_DUR  # 4.9
    T_CLOSE  = T_HOLD   + HOLD_DUR    # 5.3
    T_TOTAL  = T_CLOSE  + CLOSE_DUR   # 6.0

    _SWIRL = " ·°˙∘○◎◉●"
    _RING  = "░▒▓█"
    _CODES = [
        "C-137", "C-131", "C-132", "C-252", "C-500A", "35-C", "K-83",
        "J19ζ7", "J19α7", "J-22", "C-37", "D-99", "C-1239",
        "RICK", "MORTY", "BETH", "SUMMER", "JERRY",
        "BIRDPERSON", "SQUANCHY", "MR MEESEEKS",
        "TINY RICK", "RICK PRIME", "EVIL RICK", "DOOFUS RICK",
        "UNITY", "TAMMY", "NOOB NOOB", "EVIL MORTY",
        "CITADEL", "BLIPS & CHITZ", "PLUMBUS", "MESEEKS BOX",
        "CRONENBERG", "MICROVERSE", "MINIVERSE", "FROOPYLAND",
        "GALACTIC FED", "EARTH", "GROMFLOM",
        "WUBBA LUBBA", "GET SCHWIFTY", "PICKLE RICK",
        "SZECHUAN SAUCE", "SQUANCH", "RIGGITY RIGGITY",
        "PORTAL GUN", "NEUTRINO BOMB", "FLEEB", "SCHLEEM",
        "INTER-DIMENSIONAL", "ZIMZAR",
    ]

    particles: list = []

    def _frame(elapsed: float) -> list:
        t = elapsed

        # Reveal logo chars from center outward
        if T_REVEAL <= elapsed < T_HOLD:
            n = int(((elapsed - T_REVEAL) / REVEAL_DUR) * len(art_sorted))
            for pos in art_sorted[:n]:
                revealed.add(pos)
        elif elapsed >= T_HOLD:
            for pos in art_sorted:
                revealed.add(pos)

        # Portal radius
        if elapsed < T_OPEN:
            cur_r = 0.0
        elif elapsed < T_SPIN:
            p = (elapsed - T_OPEN) / OPEN_DUR
            cur_r = max_r * (p ** 0.55)
        elif elapsed < T_CLOSE:
            cur_r = max_r
        else:
            p = (elapsed - T_CLOSE) / CLOSE_DUR
            cur_r = max_r * max(0.0, (1.0 - p) ** 1.4)

        # Spawn dimension codes across the whole terminal from OPEN onward
        if T_OPEN <= elapsed < T_HOLD:
            rate = 0.15 if elapsed < T_SPIN else 0.40
            for _ in range(4):
                if random.random() < rate:
                    code = random.choice(_CODES)
                    pr = random.randint(1, rows - 2)
                    pc = random.randint(1, max(1, cols - len(code) - 1))
                    # Skip if pos falls inside the portal circle
                    dx = (pc + len(code) // 2 - cx) * ASPECT
                    dy = pr - cy
                    if math.sqrt(dx * dx + dy * dy) > max_r * 1.05:
                        particles.append({
                            "text": code, "row": pr, "col": pc,
                            "born": elapsed, "life": random.uniform(0.5, 1.1),
                        })

        particles[:] = [pt for pt in particles if elapsed - pt["born"] < pt["life"]]

        pmap: dict = {}
        for pt in particles:
            age = elapsed - pt["born"]
            rel = age / pt["life"]
            st  = f"bold {theme}" if 0.2 <= rel <= 0.75 else f"dim {theme}"
            for i, ch in enumerate(pt["text"]):
                pmap[(pt["row"], pt["col"] + i)] = (ch, st)

        head_idx = int(min(1.0, elapsed / SHOT_DUR) * len(beam_cells))

        lines: list = []
        for row in range(rows - 1):
            line = Text()
            for col in range(cols):
                pos = (row, col)

                # ── Shot: beam from corner ────────────────────────────────────
                if elapsed < T_OPEN:
                    if pos in beam_pos:
                        idx = beam_pos[pos]
                        if idx < head_idx:
                            dist = head_idx - 1 - idx
                            if dist == 0:
                                line.append("✦", style=f"bold {theme}")
                            elif dist <= 3:
                                line.append("●", style=f"bold {theme}")
                            elif dist <= 10:
                                line.append("○", style=theme)
                            else:
                                line.append("·", style=f"dim {theme}")
                        else:
                            line.append(" ")
                    else:
                        line.append(" ")
                    continue

                # ── Logo chars override portal vortex ─────────────────────────
                if pos in revealed:
                    line.append(art_chars[pos], style=f"bold {theme}")
                    continue

                # ── Dimension code particles ──────────────────────────────────
                if pos in pmap:
                    ch, st = pmap[pos]
                    line.append(ch, style=st)
                    continue

                # ── Portal rendering ──────────────────────────────────────────
                dx = (col - cx) * ASPECT
                dy = row - cy
                r  = math.sqrt(dx * dx + dy * dy)

                if cur_r < 1.0:
                    line.append(" ")
                    continue

                ang = math.atan2(dy, dx)
                rn  = r / cur_r

                if rn > 1.25:
                    if random.random() < 0.003:
                        line.append(random.choice("·˚✦✧"), style=f"dim {theme}")
                    else:
                        line.append(" ")

                elif rn > 1.0:
                    sv = (math.sin(ang * 7 + t * 5) + 1) / 2
                    if random.random() < sv * 0.28:
                        line.append(random.choice("✦✧˚·"), style=f"bold {theme}")
                    else:
                        line.append(" ")

                elif rn > 0.86:
                    ring_ang = (ang - t * 1.6) % 6.283
                    rv  = (math.sin(ring_ang * 12 + t * 4) + 1) / 2
                    idx = int(rv * (len(_RING) - 1))
                    st  = f"bold {theme}" if rv > 0.70 else theme
                    line.append(_RING[idx], style=st)

                else:
                    spiral = ang - t * 2.8 + rn * 14.0
                    swirl  = (math.sin(spiral * 2) + 1) / 2
                    pulse  = (math.sin(t * 5.5 - rn * 9.0) + 1) / 2
                    inten  = (swirl * 0.6 + pulse * 0.4) * (rn ** 0.35)

                    if inten < 0.07:
                        line.append(" ")
                    else:
                        idx = min(len(_SWIRL) - 1, int(inten * len(_SWIRL)))
                        ch  = _SWIRL[idx]
                        if inten > 0.72:
                            st = f"bold {theme}"
                        elif inten > 0.45:
                            st = theme
                        else:
                            st = f"dim {theme}"
                        line.append(ch, style=st)

            lines.append(line)
        return lines

    with Live(refresh_per_second=24, screen=True) as live:
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed >= T_TOTAL:
                break
            live.update(Group(*_frame(elapsed)))
            time.sleep(0.042)

    os.system("cls" if os.name == "nt" else "clear")


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


# ── Matrix + ASCII hybrid helpers ─────────────────────────────────────────────

def _prep_art_grid(
    ascii_art: str, cols: int, rows: int
) -> tuple:
    """Convert ASCII art string into a {(row, col): char} dict centered on screen."""
    lines = ascii_art.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return {}, 0, 0, 0, 0
    total_h = len(lines)
    art_h = min(total_h, rows - 4)
    v_offset = max(0, (total_h - art_h) // 2)
    lines = lines[v_offset : v_offset + art_h]
    art_w = min(max(len(l) for l in lines), cols - 4)
    row0 = max(0, (rows - art_h) // 2)
    col0 = max(0, (cols - art_w) // 2)
    chars: dict = {}
    for r, line in enumerate(lines[:art_h]):
        line_w = len(line)
        crop_offset = max(0, (line_w - art_w) // 2) if line_w > art_w else 0
        for c in range(art_w):
            src = c + crop_offset
            chars[(row0 + r, col0 + c)] = line[src] if src < line_w else " "
    return chars, art_h, art_w, row0, col0


def matrix_rain_reveal(ascii_art: str, duration: Optional[float] = None) -> None:
    """ASCII art emerges from the matrix rain; rain continues until user presses Enter."""
    import shutil
    import threading
    reveal_dur = duration if duration is not None else settings.matrix_duration
    cols, rows = shutil.get_terminal_size()
    theme = settings.color_theme

    art_chars, _, _, _, _ = _prep_art_grid(ascii_art, cols, rows)
    art_positions = sorted(
        [(r, c) for (r, c), ch in art_chars.items() if ch.strip()],
        key=lambda p: (p[0], p[1]),
    )
    random.shuffle(art_positions)

    heads = [random.randint(-rows, rows) for _ in range(cols)]
    trail_len = 8
    reveal_start = reveal_dur * 0.25
    reveal_end = reveal_dur * 0.90
    revealed: set = set()

    _key = threading.Event()

    def _wait_key() -> None:
        try:
            import readchar as _rc
            _rc.readchar()
        except Exception:
            pass
        _key.set()

    with Live(refresh_per_second=24, screen=True) as live:
        start = time.time()
        reveal_done = False
        listener_started = False

        while True:
            elapsed = time.time() - start

            if not reveal_done:
                if elapsed > reveal_start and art_positions:
                    progress = min(1.0, (elapsed - reveal_start) / (reveal_end - reveal_start))
                    target = int(progress * len(art_positions))
                    for pos in art_positions[:target]:
                        revealed.add(pos)
                if elapsed >= reveal_dur:
                    reveal_done = True
                    for pos in art_positions:
                        revealed.add(pos)

            if reveal_done and not listener_started:
                listener_started = True
                threading.Thread(target=_wait_key, daemon=True).start()

            if reveal_done and _key.is_set():
                break

            screen_lines: list[Text] = []
            for row in range(rows - 2):
                line = Text()
                for col in range(cols):
                    pos = (row, col)
                    if pos in revealed:
                        line.append(art_chars[pos], style=f"bold {theme}")
                    else:
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

            hint = Text(justify="center")
            if reveal_done:
                hint.append("  ↵  press any key to continue  ", style=f"dim {theme}")
            screen_lines.append(hint)

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


# ── Easter egg visuals ────────────────────────────────────────────────────────

_MUSIC_NOTES = "♩♪♫♬♭♮♯"

_PICKLE_ART = r"""
      ╭───────────╮
     ╭╯  ◉     ◉  ╰╮
     │    ╰───╯    │
     │   SANCHEZ   │
     ╰──────┬──────╯
            │
      ══════╪══════
            │
      ══════╪══════
            │
      ══════╪══════
"""


def show_pickle_rick() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    theme = settings.color_theme

    stages = [
        ("Analyzing C-137 DNA sequence",         theme,    1.1),
        ("Injecting chlorophyll compound",        "green",  1.4),
        ("Restructuring cellular matrix",         "cyan",   1.0),
        ("Bypassing mitochondrial suppressors",   theme,    0.9),
        ("Compressing vertebral architecture",    "green",  0.8),
        ("TRANSFORMATION COMPLETE",               "yellow", 0.8),
    ]
    total_w = sum(s[2] for s in stages)

    console.print()
    console.print(Align.center(Panel(
        "[bold yellow]  RICKINATOR v3.0 — MUTAGENIC SEQUENCE  [/bold yellow]",
        border_style=theme, padding=(0, 4),
    )))
    console.print()

    with Progress(
        SpinnerColumn(style="bold green"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=38, style="dim green", complete_style="bold green"),
        TextColumn("[bold green]{task.percentage:>3.0f}%"),
        console=console,
        transient=False,
    ) as prog:
        task = prog.add_task(stages[0][0], total=100)
        for desc, color, weight in stages:
            prog.update(task, description=f"[{color}]{desc}[/{color}]")
            segment = (weight / total_w) * 100
            steps = max(1, int(segment / 0.6))
            for _ in range(steps):
                time.sleep(0.018)
                prog.advance(task, segment / steps)
        prog.update(task, completed=100,
                    description="[bold green]TRANSFORMATION COMPLETE[/bold green]")
        time.sleep(0.4)

    console.print()
    for line in _PICKLE_ART.split("\n"):
        console.print(f"  [bold green]{line}[/bold green]")
        if settings.effects_enabled:
            time.sleep(0.07)
    console.print()
    typing_effect("  > I turned myself into a pickle, Morty!", "green", delay=0.035)
    typing_effect("  > Boom! Big reveal — I'M PICKLE RIIIICK!!!", "bold yellow", delay=0.055)
    _sleep(2.0)


def show_wubba_lubba() -> None:
    theme = settings.color_theme
    from pyfiglet import Figlet
    fig = Figlet(font=settings.figlet_font)

    words = [
        ("WUBBA",   "bold cyan"),
        ("LUBBA",   "bold yellow"),
        ("DUB",     f"bold {theme}"),
        ("DUB !!!", "bold white"),
    ]
    for word, style in words:
        os.system("cls" if os.name == "nt" else "clear")
        console.print()
        console.print(Text(fig.renderText(word), style=style), justify="center")
        time.sleep(0.28)

    os.system("cls" if os.name == "nt" else "clear")
    console.print()
    console.print(Text(fig.renderText("WUBBA LUBBA"), style=f"bold {theme}"), justify="center")
    console.print(Text(fig.renderText("DUB  DUB !!"), style="bold yellow"), justify="center")
    console.print()
    console.print(Align.center(Panel(
        f"[dim {theme}]— Birdperson translation —[/dim {theme}]\n\n"
        "[bold white]I am in great pain, please help me.[/bold white]",
        border_style=theme, padding=(1, 6),
    )))
    _sleep(2.5)


def show_portal_secret() -> None:
    import shutil
    import threading
    theme = settings.color_theme
    cols, rows = shutil.get_terminal_size()
    cx, cy = cols / 2.0, rows / 2.0
    ASPECT  = 0.45
    max_r   = min(rows * 0.38, cols * ASPECT * 0.40)
    OPEN_DUR  = 1.2
    CLOSE_DUR = 0.9

    _SWIRL = " ·°˙∘○◎◉●"
    _RING  = "░▒▓█"

    phase       = "opening"
    open_start  = time.time()
    close_start = None

    _key = threading.Event()

    def _wait_key() -> None:
        try:
            import readchar as _rc
            _rc.readchar()
        except Exception:
            pass
        _key.set()

    with Live(refresh_per_second=24, screen=True) as live:
        while True:
            now = time.time()
            t   = now - open_start          # always-increasing for swirl animation

            if phase == "opening":
                cur_r = max_r * min(1.0, (t / OPEN_DUR) ** 0.6)
                if t >= OPEN_DUR:
                    phase = "spinning"
                    threading.Thread(target=_wait_key, daemon=True).start()
            elif phase == "spinning":
                cur_r = max_r
                if _key.is_set():
                    phase       = "closing"
                    close_start = now
            else:
                p     = now - close_start
                cur_r = max_r * (max(0.0, 1.0 - p / CLOSE_DUR) ** 1.5)
                if p >= CLOSE_DUR:
                    break

            lines = []
            for row in range(rows - 2):
                line = Text()
                for col in range(cols):
                    dx = (col - cx) * ASPECT
                    dy = row - cy
                    r  = math.sqrt(dx * dx + dy * dy)
                    if cur_r < 1.0:
                        line.append(" ")
                        continue
                    ang = math.atan2(dy, dx)
                    rn  = r / cur_r
                    if rn > 1.25:
                        if random.random() < 0.003:
                            line.append(random.choice("·˚✦"), style=f"dim {theme}")
                        else:
                            line.append(" ")
                    elif rn > 1.0:
                        sv = (math.sin(ang * 7 + t * 5) + 1) / 2
                        if random.random() < sv * 0.25:
                            line.append(random.choice("✦✧˚"), style=f"bold {theme}")
                        else:
                            line.append(" ")
                    elif rn > 0.86:
                        ra  = (ang - t * 1.6) % 6.283
                        rv  = (math.sin(ra * 12 + t * 4) + 1) / 2
                        idx = int(rv * (len(_RING) - 1))
                        st  = f"bold {theme}" if rv > 0.70 else theme
                        line.append(_RING[idx], style=st)
                    else:
                        sp = ang - t * 2.8 + rn * 14.0
                        sw = (math.sin(sp * 2) + 1) / 2
                        pu = (math.sin(t * 5.5 - rn * 9.0) + 1) / 2
                        iv = (sw * 0.6 + pu * 0.4) * (rn ** 0.35)
                        if iv < 0.07:
                            line.append(" ")
                        else:
                            ch = _SWIRL[min(len(_SWIRL) - 1, int(iv * len(_SWIRL)))]
                            if iv > 0.72:
                                st = f"bold {theme}"
                            elif iv > 0.45:
                                st = theme
                            else:
                                st = f"dim {theme}"
                            line.append(ch, style=st)
                lines.append(line)

            hint = Text(justify="center")
            if phase == "spinning":
                hint.append("  press any key to close the portal  ", style=f"dim {theme}")
            lines.append(hint)

            live.update(Group(*lines))
            time.sleep(0.042)

    os.system("cls" if os.name == "nt" else "clear")


def show_get_schwifty() -> None:
    import shutil
    import subprocess
    from pathlib import Path
    theme = settings.color_theme
    cols, rows = shutil.get_terminal_size()

    music_path = Path(__file__).parent / "schwifty.mp3"
    audio_proc = None
    if music_path.exists():
        try:
            audio_proc = subprocess.Popen(
                ["afplay", str(music_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            audio_proc = None

    fallback_end = time.time() + 4.0

    with Live(refresh_per_second=24, screen=True) as live:
        start = time.time()
        while True:
            if audio_proc is not None:
                if audio_proc.poll() is not None:
                    break
            elif time.time() > fallback_end:
                break

            elapsed = time.time() - start
            lines = []
            for row in range(rows - 1):
                line = Text()
                for col in range(cols):
                    w1 = math.sin(col * 0.25 + elapsed * 6.0)
                    w2 = math.sin(col * 0.10 + elapsed * 3.5 + row * 0.4)
                    iv = (w1 + w2) / 2
                    if iv > 0.55 and random.random() < 0.38:
                        ch = _MUSIC_NOTES[int(abs(iv * len(_MUSIC_NOTES))) % len(_MUSIC_NOTES)]
                        if iv > 0.85:
                            line.append(ch, style="bold yellow")
                        elif iv > 0.70:
                            line.append(ch, style=f"bold {theme}")
                        else:
                            line.append(ch, style=theme)
                    else:
                        line.append(" ")
                lines.append(line)
            live.update(Group(*lines))
            time.sleep(0.042)

    os.system("cls" if os.name == "nt" else "clear")
    from pyfiglet import Figlet
    try:
        fig = Figlet(font="doom")
        # sanity-check width — if "GET" renders wider than 80% of terminal, fall back
        if max(len(l) for l in fig.renderText("GET").split("\n")) > int(cols * 0.8):
            raise ValueError
    except Exception:
        fig = Figlet(font="big")
    console.print()
    console.print(Text(fig.renderText("GET"), style=f"bold {theme}"), justify="center")
    console.print(Text(fig.renderText("SCHWIFTY"), style="bold yellow"), justify="center")
    console.print()
    typing_effect("  ♪  Rick Sanchez performing live — Dimension C-137  ♪", "yellow", delay=0.025)
    typing_effect("  ♫  Earth saved via interdimensional anthem  ♫", f"dim {theme}", delay=0.020)
    _sleep(2.0)


def show_szechuan_sauce() -> None:
    theme = settings.color_theme
    os.system("cls" if os.name == "nt" else "clear")
    console.print()
    console.print(Align.center(Panel(
        "[bold yellow]McDIMENSION'S™[/bold yellow]\n"
        "[dim white]Interdimensional Fast Food — Est. Dimension C-137[/dim white]",
        border_style="yellow", padding=(0, 8),
    )))
    console.print()
    typing_effect("  > Scanning McNugget sauce inventory across 826 dimensions...", theme, delay=0.015)
    console.print()

    dims = [
        "C-137", "J19ζ7", "K-83", "35-C", "C-500A",
        "J-22", "C-1239", "Froopyland", "Citadel of Ricks", "C-131",
    ]
    with Progress(
        SpinnerColumn(style="bold yellow"),
        TextColumn("[white]Scanning [yellow]{task.description}[/yellow]"),
        BarColumn(bar_width=28, style="dim yellow", complete_style="yellow"),
        TextColumn("[bold red]OUT OF STOCK[/bold red]"),
        console=console,
    ) as prog:
        for dim in dims:
            t = prog.add_task(f"{dim:<26}", total=100)
            for _ in range(40):
                time.sleep(0.008)
                prog.advance(t, 2.5)
            prog.update(t, completed=100)

    console.print()
    console.print(Align.center(Panel(
        "[bold red]SZECHUAN McNUGGET SAUCE[/bold red]\n"
        "[bold white]DISCONTINUED ACROSS ALL 826 KNOWN DIMENSIONS[/bold white]\n\n"
        "[dim white]Original Mulan promotion — 1998. Unavailable in any timeline.[/dim white]",
        border_style="red", padding=(1, 4),
    )))
    console.print()
    typing_effect("  > That's my series arc, Morty!", "yellow", delay=0.04)
    typing_effect("  > If it takes nine seasons...", "yellow", delay=0.03)
    typing_effect("  > I want that Mulan McNugget Sauce, Morty!", "bold red", delay=0.05)
    _sleep(2.0)


def show_rickroll() -> None:
    import shutil
    import subprocess
    import threading
    from pathlib import Path
    theme = settings.color_theme
    cols, rows = shutil.get_terminal_size()

    # Start music if file exists
    music_path = Path(__file__).parent / "evilmorty.mp3"
    audio_proc = None
    if music_path.exists():
        try:
            audio_proc = subprocess.Popen(
                ["afplay", str(music_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            audio_proc = None

    # Evil Morty palette — override theme with red/dark
    evil_hi  = "bold red"
    evil_mid = "red"
    evil_lo  = "dim red"

    bar_count = cols // 3
    bars = [random.random() for _ in range(bar_count)]

    _key = threading.Event()

    def _wait_key() -> None:
        try:
            import readchar as _rc
            _rc.readchar()
        except Exception:
            pass
        _key.set()

    threading.Thread(target=_wait_key, daemon=True).start()

    with Live(refresh_per_second=24, screen=True) as live:
        start = time.time()
        while not _key.is_set():
            elapsed = time.time() - start
            for i in range(bar_count):
                target = (math.sin(i * 0.6 + elapsed * 3.5) + 1) / 2 * 0.7 + random.uniform(0, 0.3)
                bars[i] += (target - bars[i]) * 0.3
                bars[i] = max(0.02, min(1.0, bars[i]))

            bar_h = rows - 4
            lines = []
            for row in range(bar_h):
                line = Text()
                threshold = 1.0 - row / bar_h
                for height in bars:
                    diff = height - threshold
                    if diff > 0.15:
                        line.append("█  ", style=evil_hi)
                    elif diff > 0.0:
                        line.append("▓  ", style=evil_mid)
                    elif diff > -0.08:
                        line.append("░  ", style=evil_lo)
                    else:
                        line.append("   ")
                lines.append(line)

            note_row = Text()
            for _ in range(cols):
                if random.random() < 0.06:
                    note_row.append(random.choice(_MUSIC_NOTES), style=evil_lo)
                else:
                    note_row.append(" ")
            lines.append(note_row)

            hint = Text(justify="center")
            hint.append(
                "  ✖  EVIL MORTY HAS TAKEN CONTROL  ✖   ",
                style=evil_hi,
            )
            hint.append("press any key to escape", style=evil_lo)
            lines.append(hint)

            live.update(Group(*lines))
            time.sleep(0.042)

    if audio_proc and audio_proc.poll() is None:
        audio_proc.terminate()

    os.system("cls" if os.name == "nt" else "clear")
