from __future__ import annotations
import os
from pathlib import Path
import httpx

async def download_image(url: str, filename: str) -> str:
    """Download an image from a URL to ~/Pictures/Cosmo/."""
    if not url:
        raise ValueError("No URL provided")
        
    save_dir = Path.home() / "Pictures" / "Cosmo"
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_filename = "".join([c for c in filename if c.isalnum() or c in "._- "]).strip()
    if not safe_filename:
        safe_filename = "cosmo_image"
        
    ext = url.split(".")[-1].split("?")[0]
    if len(ext) > 4:  # Handle cases where extension isn't clear
        ext = "jpg"
    
    full_path = save_dir / f"{safe_filename}.{ext}"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        full_path.write_bytes(r.content)
        
    return str(full_path)
