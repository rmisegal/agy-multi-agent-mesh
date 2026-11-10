# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""``python -m agymesh`` (used by the hub launcher) - same as the ``agymesh`` command."""

from .cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
