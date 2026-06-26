"""Entry point — parse flags, boot, run."""
from __future__ import annotations

import sys

from utils import ensure_dirs


def _parse_flags() -> dict:
    args = sys.argv[1:]
    return {
        "classic":     "--classic" in args or "-c" in args,
        "no_effects":  "--no-effects" in args or "--fast" in args,
        "no_boot":     "--no-boot" in args,
    }


def main() -> None:
    ensure_dirs()
    flags = _parse_flags()

    # Override effects before importing anything that reads them
    if flags["no_effects"]:
        from settings import settings
        settings.override("effects_enabled", False)

    # Classic mode: skip the whole TUI and run the original behaviour
    if flags["classic"]:
        _run_classic()
        return

    from effects import boot_screen
    from menu import run_app

    if not flags["no_boot"]:
        boot_screen()

    try:
        run_app()
    except KeyboardInterrupt:
        _farewell()


def _run_classic() -> None:
    """Exact original behaviour: random char → figlet name → ASCII art."""
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    from pyfiglet import Figlet
    from api import RickAndMortyAPI, APIError
    from ascii_engine import image_url_to_ascii
    from settings import settings

    try:
        char = RickAndMortyAPI.get_random_character()
    except APIError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    fig = Figlet(font=settings.figlet_font)
    print(fig.renderText(char.name))
    print(image_url_to_ascii(char.image))


def _farewell() -> None:
    from effects import typing_effect
    from settings import settings
    print()
    typing_effect("  Wubba lubba dub dub!", settings.color_theme, delay=0.04)
    print()


if __name__ == "__main__":
    main()
