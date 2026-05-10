from __future__ import annotations

import mimetypes
from pathlib import Path
from urllib.parse import urlparse

import httpx

MAX_IMAGE_BYTES = 25 * 1024 * 1024


def _safe_suffix(url: str, content_type: str) -> str:
    path_suffix = Path(urlparse(url).path).suffix.lower()
    if path_suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return path_suffix
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
    if guessed in {".jpe"}:
        return ".jpg"
    if guessed in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return guessed
    return ".jpg"


async def download_image(url: str, filename: str) -> str:
    """Download an image from a URL to ~/Pictures/Cosmo/."""
    if not url:
        raise ValueError("No URL provided")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Only HTTP(S) image URLs can be saved")

    save_dir = Path.home() / "Pictures" / "Cosmo"
    save_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_filename = "".join([c for c in filename if c.isalnum() or c in "._- "]).strip()
    if not safe_filename:
        safe_filename = "cosmo_image"
    safe_filename = safe_filename[:80].rstrip(" .")

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        if not content_type.lower().startswith("image/"):
            raise ValueError("URL did not return an image")
        content_length = r.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > MAX_IMAGE_BYTES:
            raise ValueError("Image is too large to save")
        if len(r.content) > MAX_IMAGE_BYTES:
            raise ValueError("Image is too large to save")

        full_path = save_dir / f"{safe_filename}{_safe_suffix(str(r.url), content_type)}"
        full_path.write_bytes(r.content)

    return str(full_path)
