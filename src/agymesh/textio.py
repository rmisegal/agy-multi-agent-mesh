# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Text helpers shared by the SDK and the CLI."""

from __future__ import annotations

from pathlib import Path


def read_text_any(path: str | Path) -> str:
    """Read an answer file whatever wrote it: UTF-8, UTF-8 with BOM, or UTF-16 (PowerShell 5)."""
    raw = Path(path).read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16").strip()
    return raw.decode("utf-8-sig", errors="replace").strip()


def fill(template: str, **values: str) -> str:
    """Replace ``{{key}}`` placeholders; unknown placeholders are left untouched."""
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template
