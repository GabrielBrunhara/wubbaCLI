"""Disk-based image cache — images are downloaded exactly once."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

import requests
from PIL import Image
from io import BytesIO

from utils import CACHE_DIR


def _url_to_path(url: str) -> Path:
    digest = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{digest}.png"


def get_image(url: str) -> Image.Image:
    """Return a PIL Image from cache or download-and-cache it."""
    path = _url_to_path(url)
    if path.exists():
        return Image.open(path).copy()
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))
    img.save(path, format="PNG")
    return img.copy()


def is_cached(url: str) -> bool:
    return _url_to_path(url).exists()


def cache_stats() -> Dict[str, float]:
    files = list(CACHE_DIR.glob("*.png"))
    total_bytes = sum(f.stat().st_size for f in files)
    return {
        "count":   len(files),
        "size_mb": round(total_bytes / 1_048_576, 2),
    }


def clear_cache() -> int:
    files = list(CACHE_DIR.glob("*.png"))
    for f in files:
        f.unlink(missing_ok=True)
    return len(files)
