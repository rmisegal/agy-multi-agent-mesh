# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Build the single-file agymesh USER_MANUAL deck.

1. Concatenate parts/*.html (sorted) into USER_MANUAL_slides.src.html.
2. Inline {{IMG:name}} placeholders as base64 PNG data URIs.
3. Inject the copyright watermark before every </section>.
4. Validate slide count, watermark count and leftover placeholders.

Usage:  python -I -X utf8 _src/build.py
"""
import base64
import re
import sys
from pathlib import Path

STEM = "USER_MANUAL"
SLIDE_COUNT = 12
WATERMARK = ('<div class="wm">© 2026 כל הזכויות שמורות לד״ר יורם סגל, '
             'גל טכנולוגיות בינה מלאכותית בע״מ</div>')

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
PARTS = SRC / "parts"
IMG = SRC / "img"


def assemble() -> str:
    parts = sorted(PARTS.glob("*.html"))
    if not parts:
        sys.exit("ERROR: no parts found in " + str(PARTS))
    text = "\n".join(p.read_text(encoding="utf-8") for p in parts)
    (SRC / f"{STEM}_slides.src.html").write_text(text, encoding="utf-8")
    return text


def inline_images(text: str) -> str:
    def repl(m: re.Match) -> str:
        name = m.group(1)
        path = IMG / f"{name}.png"
        if not path.exists():
            sys.exit(f"ERROR: image not found: {path}")
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return "data:image/png;base64," + data

    return re.sub(r"\{\{IMG:([\w\-]+)\}\}", repl, text)


def add_watermarks(text: str) -> str:
    return text.replace("</section>", WATERMARK + "\n</section>")


def validate(text: str) -> int:
    errors = []
    if "{{IMG:" in text:
        errors.append("unresolved {{IMG:...}} placeholder")
    slides = len(re.findall(r'<section class="slide"', text))
    marks = text.count('<div class="wm">')
    if slides != SLIDE_COUNT:
        errors.append(f"slide count {slides} != {SLIDE_COUNT}")
    if marks != slides:
        errors.append(f"watermark count {marks} != slide count {slides}")
    for i, sec in enumerate(re.findall(r'<section class="slide".*?</section>', text, re.S), 1):
        for tag in ("div", "span", "table", "pre", "svg"):
            opened = len(re.findall(rf"<{tag}[\s>]", sec))
            closed = sec.count(f"</{tag}>")
            if opened != closed:
                errors.append(f"slide {i}: <{tag}> opened {opened}, closed {closed}")
    if errors:
        for e in errors:
            print("ERROR:", e)
        sys.exit(1)
    return slides


def main() -> None:
    text = add_watermarks(inline_images(assemble()))
    slides = validate(text)
    out = OUT / f"{STEM}_slides.html"
    out.write_text(text, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"OK: {slides} slides, watermark on all, {size_kb:,.0f} KB -> {out}")


if __name__ == "__main__":
    main()
