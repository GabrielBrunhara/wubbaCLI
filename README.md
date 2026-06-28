```
██╗    ██╗██╗   ██╗██████╗ ██████╗  █████╗  ██████╗██╗     ██╗
██║    ██║██║   ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝██║     ██║
██║ █╗ ██║██║   ██║██████╔╝██████╔╝███████║██║     ██║     ██║
██║███╗██║██║   ██║██╔══██╗██╔══██╗██╔══██║██║     ██║     ██║
╚███╔███╔╝╚██████╔╝██████╔╝██████╔╝██║  ██║╚██████╗███████╗██║
 ╚══╝╚══╝  ╚═════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝
```

<div align="center">

**A Rick and Morty terminal app that makes people ask _"Wait... this is Python?"_**

[![Python](https://img.shields.io/badge/Python-3.10%2B-00ff41?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Rich](https://img.shields.io/badge/Rich-13.7%2B-00ff41?style=flat-square)](https://github.com/Textualize/rich)
[![Rick and Morty API](https://img.shields.io/badge/API-Rick%20%26%20Morty-00ff41?style=flat-square)](https://rickandmortyapi.com)
[![License](https://img.shields.io/badge/License-MIT-00ff41?style=flat-square)](LICENSE)

</div>

---

## What is this

WubbaCLI is a full TUI application built on top of the [Rick and Morty API](https://rickandmortyapi.com), with a premium interface powered by Rich.

This is not a script. It's software.

Animated portal boot screen. Navigable menu. Real-time ASCII art generation. Games. Favorites. History. Export. Matrix rain effects. Local cache. Easter eggs.

---

## Installation

```bash
git clone https://github.com/your-username/wubba-cli
cd wubba-cli

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

> Requires Python 3.10+ and an internet connection to fetch characters.

---

## Usage

```bash
# Full mode (animated boot screen + interactive menu)
python main.py

# Classic mode — random character, figlet name, ASCII art, no TUI
python main.py --classic

# Skip animations (faster, useful on slow terminals)
python main.py --no-effects

# Skip the boot screen and go straight to the menu
python main.py --no-boot
```

---

## Boot Screen

The default **epic** mode fires a laser beam from the bottom-left corner of the screen toward the center, where an interdimensional portal opens — animated with polar coordinates, a spinning vortex, and particles of series references scattered across the terminal. The WubbaCLI logo materializes from inside the portal before it closes.

The **classic** mode displays a static banner with a boot log and progress bar.

Boot style can be changed in **Settings → B**.

---

## Main Menu

```
╭──────────────────────  MAIN MENU  ──────────────────────╮
│                                                         │
│    C   Character      Browse any character              │
│    B   Search         Find a character by name          │
│    E   Episode        Explore a random episode          │
│    M   Matrix Reveal  ASCII art emerges from the rain   │
│    G   Games          Mini-games and trivia             │
│    F   Favorites      Your bookmarked characters        │
│    H   History        Recently viewed characters        │
│    S   Settings       Configure appearance              │
│    Q   Quit           Wubba lubba dub dub               │
│                                                         │
╰──────────────────── Type a letter + Enter ──────────────╯
```

---

## Features

### Character Viewer
ASCII art on the left, info panel on the right. Available actions:
- `F` — add / remove from favorites
- `T` — toggle ASCII art opacity (50% / 100%)
- `E` — export (TXT or HTML)
- `S` — full character stats
- `Q` — back

### Search
Search by name. One result: opens directly. Multiple results: numbered table with status and episode count.

### Episode
Picks a random episode, displays its code, air date, and character list. Open any character from the list by number.

### Matrix Reveal
Full-screen matrix-style character rain. A random character's ASCII art gradually emerges from the rain. Press Enter to open the full Character Viewer.

### Games

| Game | Description |
|---|---|
| **G — Guess Who** | See the ASCII art, pick the name from 4 options |
| **A — Alive or Dead** | See the name and data, guess the status |
| **S — Species Roulette** | See the character, guess their species |
| **E — Episode Counter** | Guess how many episodes the character appeared in |
| **R — Random Game** | Let the universe decide |
| **P — Scores** | Persistent scoreboard per game |

### Favorites & History
- **Favorites** — persisted in `favorites.json`
- **History** — last 50 viewed characters, persisted in `history.json`

### Export
Any ASCII art can be exported to:
- **TXT** — plain text file with character metadata
- **HTML** — self-contained page with dark background and monospace font

Files saved to `exports/`.

### Cache
Images are downloaded once and stored in `ascii_cache/`. Can be cleared from Settings.

### Settings

| Key | Option | Values |
|---|---|---|
| W | ASCII Width | 40 – 300 |
| A | Auto Width | ON / OFF |
| C | Charset | `detailed` `simple` `blocks` `binary` `dense` `matrix` `braille` |
| T | Color Theme | `green` `cyan` `amber` `red` `purple` `white` `blue` |
| F | Figlet Font | `ansi_shadow` `colossal` `doom` `epic` `slant` `big` `block` `digital` and more |
| E | Effects | ON / OFF |
| B | Boot Style | `epic` / `classic` |
| S | Typing Speed | 0 – 0.2s per character |
| R | Reset Defaults | — |
| X | Clear Cache | — |

Settings are persisted to `config.json`. The title and portal logo in the boot animation both use the selected figlet font.

---

## Easter Eggs

Type any of the following terms at the search prompt:

```
pickle rick
wubba lubba dub dub
portal
get schwifty
szechuan
rickroll
```

---

## Project Structure

```
wubba-cli/
│
├── main.py          # Entry point, CLI flag parsing
├── menu.py          # Main loop and mode dispatch
│
├── api.py           # Rick and Morty API client
├── ascii_engine.py  # Image → ASCII conversion pipeline
├── cache.py         # Local image cache
│
├── effects.py       # Boot screen (epic/classic), matrix rain, typewriter
├── ui.py            # All Rich panels and prompts
├── export.py        # TXT and HTML export
│
├── settings.py      # Typed settings with persistence
├── favorites.py     # Favorites manager
├── history.py       # View history
├── games.py         # Mini-games and score tracker
├── utils.py         # Path constants and OS helpers
│
├── config.json      # User preferences (auto-generated)
├── requirements.txt
│
├── ascii_cache/     # Image cache (auto-generated)
└── exports/         # Exported files (auto-generated)
```

---

## Dependencies

```
requests    — HTTP client
Pillow      — Image processing
rich        — TUI interface
pyfiglet    — Text ASCII art
colorama    — Cross-platform color support
readchar    — Single-character input
```

---

## License

MIT — do whatever you want, just don't destroy any alternate dimensions in the process.

---

<div align="center">

*"Nobody exists on purpose. Nobody belongs anywhere. Everybody's gonna die. Come watch TV."*

**— Morty Smith**

</div>
