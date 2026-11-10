# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""agymesh - session-to-session IPC for Antigravity CLI (agy) sessions.

Public API: :class:`AgyMesh` (the SDK facade) and ``__version__``.
"""

from .sdk import AgyMesh
from .version import __version__

__all__ = ["AgyMesh", "__version__"]
