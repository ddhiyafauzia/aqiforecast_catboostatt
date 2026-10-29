"""Bundled brand assets, served as cached base64 data URIs so the page needs no extra requests."""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

from aqi.config import BASE_DIR

ASSETS_DIR = BASE_DIR / "assets"
_MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


@lru_cache(maxsize=None)
def file_data_uri(path: Path) -> str:
    payload = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:{_MIME[Path(path).suffix.lower()]};base64,{payload}"


@lru_cache(maxsize=None)
def data_uri(name: str) -> str:
    return file_data_uri(ASSETS_DIR / name)


def read_text(name: str) -> str:
    return (ASSETS_DIR / name).read_text(encoding="utf-8")


def university_logo_uri() -> str:
    """The real ``university_logo.png`` when present, otherwise the bundled USH emblem."""
    custom = BASE_DIR / "university_logo.png"
    return file_data_uri(custom) if custom.exists() else data_uri("ush_emblem.svg")
