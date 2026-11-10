# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Entry point of the ``agymesh`` command."""

from __future__ import annotations

import contextlib
import sys

from ..config import MeshConfig
from ..errors import MeshError
from ..sdk import AgyMesh
from .handlers import Handlers
from .parser import build_parser


def utf8_console() -> None:
    """Hebrew output must not crash a cp1252 Windows console."""
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None, mesh: AgyMesh | None = None) -> int:
    utf8_console()
    args = build_parser().parse_args(argv)
    try:
        mesh = mesh or AgyMesh(MeshConfig.load(args.config_dir), args.team, args.allow_external)
        return Handlers(mesh).run(args)
    except (MeshError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
