"""Converts PIL images to ASCII art with multiple charset presets."""
from __future__ import annotations

from PIL import Image

from cache import get_image
from settings import settings


# ── Core pipeline ─────────────────────────────────────────────────────────────

def resize_image(
    image: Image.Image,
    new_width: int,
    aspect_fix: float = 0.55,
) -> Image.Image:
    """Resize preserving aspect ratio, corrected for terminal cell height."""
    w, h = image.size
    new_height = int(new_width * (h / w) * aspect_fix)
    return image.resize((new_width, max(1, new_height)))


def to_grayscale(image: Image.Image) -> Image.Image:
    return image.convert("L")


def pixels_to_ascii(image: Image.Image, charset: str) -> str:
    pixels = list(image.getdata())
    scale = len(charset) - 1
    return "".join(charset[p * scale // 255] for p in pixels)


def image_to_ascii(
    image: Image.Image,
    width: int,
    charset: str,
) -> str:
    """Full pipeline: resize → grayscale → ASCII string."""
    img = resize_image(image, width)
    img = to_grayscale(img)
    raw = pixels_to_ascii(img, charset)
    return "\n".join(raw[i : i + width] for i in range(0, len(raw), width))


def image_url_to_ascii(
    url: str,
    width: int | None = None,
    charset: str | None = None,
) -> str:
    """Fetch from cache (or download) and convert to ASCII art."""
    w = width if width is not None else settings.display_width
    cs = charset if charset is not None else settings.charset
    image = get_image(url)
    return image_to_ascii(image, w, cs)
