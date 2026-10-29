"""Brand assets as cached, size-optimised base64 data URIs (no extra HTTP requests, no layout flash)."""
from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

from aqi.config import BASE_DIR, BRAND_LOGOS, LOGO_DIR

ASSETS_DIR = BASE_DIR / "assets"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".svg")
_MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".webp": "image/webp"}
LOGO_MAX_WIDTH = 360
PHOTO_MAX_WIDTH = 1400


def _uri(mime: str, payload: bytes) -> str:
    return f"data:{mime};base64,{base64.b64encode(payload).decode('ascii')}"


def _optimised(path: Path, max_width: int) -> Tuple[str, bytes]:
    """Downscale raster images with Pillow when available; otherwise return the file untouched."""
    raw, mime = path.read_bytes(), _MIME[path.suffix.lower()]
    if path.suffix.lower() == ".svg":
        return mime, raw
    try:
        from PIL import Image
    except ImportError:
        return mime, raw
    image = Image.open(io.BytesIO(raw))
    if image.width > max_width:
        image = image.resize((max_width, round(image.height * max_width / image.width)), Image.LANCZOS)
    buffer = io.BytesIO()
    if mime == "image/jpeg":
        image.convert("RGB").save(buffer, "JPEG", quality=80, optimize=True)
        return "image/jpeg", buffer.getvalue()
    image.save(buffer, "PNG", optimize=True)
    return "image/png", buffer.getvalue()


@lru_cache(maxsize=None)
def _cached_uri(path: Path, max_width: int, mtime_ns: int) -> str:
    return _uri(*_optimised(path, max_width))


def file_data_uri(path: Path, max_width: int = LOGO_MAX_WIDTH) -> str:
    path = Path(path)
    return _cached_uri(path, max_width, path.stat().st_mtime_ns)


@lru_cache(maxsize=None)
def data_uri(name: str) -> str:
    """Bundled asset from ``assets/`` (raises FileNotFoundError when missing)."""
    return file_data_uri(ASSETS_DIR / name)


def read_text(name: str) -> str:
    return (ASSETS_DIR / name).read_text(encoding="utf-8")


def find_image(directory: Path, stem: str) -> Optional[Path]:
    """Case-insensitive lookup of ``<stem>.<any image extension>``."""
    directory = Path(directory)
    if not directory.is_dir():
        return None
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.stem.lower() == stem.lower() and path.suffix.lower() in IMAGE_EXTENSIONS:
            return path
    return None


def brand_logos(logo_dir: Path = LOGO_DIR) -> List[Tuple[str, str]]:
    """(alt, data-URI) of each logo present in ``logo_dir``; the USH emblem stands in when its file is absent."""
    logos = []
    for alt, stem in BRAND_LOGOS:
        path = find_image(logo_dir, stem)
        if path is not None:
            logos.append((alt, file_data_uri(path)))
        elif stem == "ushlogo":
            logos.append((alt, data_uri("ush_emblem.svg")))
    return logos


def photo_data_uri(directory: Path, stem: str, max_width: int = PHOTO_MAX_WIDTH) -> Optional[str]:
    path = find_image(directory, stem)
    return file_data_uri(path, max_width) if path else None
