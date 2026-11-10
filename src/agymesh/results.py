# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""ResultWriter: save a merged mesh result as UTF-8 Markdown + an RTL-aware HTML page.

Terminals on Windows (conhost / Windows Terminal) have no bidirectional text support, so Hebrew
shows in reverse letter order inside agy. The browser renders it correctly: every block uses
``dir="auto"``, so Hebrew paragraphs are right-to-left and ASCII art stays left-to-right.
"""

from __future__ import annotations

import html
import os
import re
import time
from collections.abc import Callable
from pathlib import Path

from .orchestrate import Reply
from .version import COPYRIGHT, __version__

FENCE = re.compile(r"^\s*(```|~~~)")

PAGE = """<!doctype html>
<html lang="he"><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:2em auto;padding:0 1em}}
section{{border:1px solid #ccc;border-radius:8px;padding:.5em 1em;margin:1em 0}}
.txt{{font-family:Consolas,'Courier New',monospace;font-size:15px}}
.ln{{white-space:pre-wrap;unicode-bidi:plaintext;min-height:1.2em}}
.meta{{color:#666;font-size:13px}} .missing{{color:#b00}}</style></head>
<body><h1 dir="auto">{title}</h1>{sections}
<footer class="meta">agymesh {version} &middot; {copyright}</footer></body></html>
"""


def _default_opener(path: Path) -> None:  # pragma: no cover - opens a browser window
    if hasattr(os, "startfile"):
        os.startfile(str(path))  # type: ignore[attr-defined]


def slug(text: str) -> str:
    return re.sub(r"[^\w-]+", "-", text, flags=re.UNICODE).strip("-")[:40] or "result"


class ResultWriter:
    def __init__(self, folder: Path, open_result: bool,
                 opener: Callable[[Path], None] = _default_opener,
                 stamp: Callable[[], str] = lambda: time.strftime("%Y%m%d-%H%M%S")) -> None:
        self.folder = Path(folder)
        self.open_result = open_result
        self.opener = opener
        self.stamp = stamp

    def markdown(self, title: str, results: dict[str, Reply]) -> str:
        parts = [f"# {title}"]
        for peer, r in results.items():
            parts += [f"\n## {peer} ({r.answered_by or 'no answer'})\n",
                      r.text if r.ok else f"_no answer: {r.error}_"]
        parts.append(f"\n---\n_agymesh {__version__} - {COPYRIGHT}_")
        return "\n".join(parts) + "\n"

    @staticmethod
    def lines_html(text: str) -> str:
        """One ``dir="auto"`` block PER LINE: each line takes its direction from its own first
        strong letter, so a Hebrew line is RTL (parentheses mirror correctly) and ASCII-art
        lines stay LTR. A single block-level ``dir="auto"`` used the first strong letter of the
        whole answer (e.g. the Latin ``text`` of a Markdown fence) for every line."""
        rows = [line for line in text.splitlines() if not FENCE.match(line)]
        return "".join(f'<div class="ln" dir="auto">{html.escape(line) or "&nbsp;"}</div>'
                       for line in rows)

    def html_page(self, title: str, results: dict[str, Reply]) -> str:
        blocks = []
        for peer, r in results.items():
            body = (f'<div class="txt">{self.lines_html(r.text)}</div>' if r.ok else
                    f'<p class="missing">no answer: {html.escape(r.error)}</p>')
            blocks.append(f'<section><h2>{html.escape(peer)}</h2><div class="meta">'
                          f'{html.escape(r.answered_by or "no answer")}</div>{body}</section>')
        return PAGE.format(title=html.escape(title), sections="".join(blocks),
                           version=__version__, copyright=html.escape(COPYRIGHT))

    def save(self, title: str, results: dict[str, Reply]) -> Path:
        self.folder.mkdir(parents=True, exist_ok=True)
        base = self.folder / f"{self.stamp()}-{slug(title)}"
        base.with_suffix(".md").write_text(self.markdown(title, results), encoding="utf-8")
        page = base.with_suffix(".html")
        page.write_text(self.html_page(title, results), encoding="utf-8")
        if self.open_result:
            self.opener(page)
        return page
