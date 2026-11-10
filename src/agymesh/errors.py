# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Exception hierarchy. Every error carries a short machine code and a plain-language message."""

from __future__ import annotations

from .constants import ERR_NOT_IN_SESSION


class MeshError(Exception):
    """Base error of the mesh; ``code`` travels over the wire in hub replies."""

    code = "mesh_error"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class ConfigError(MeshError):
    """A config or team file is missing, malformed or of an unsupported version."""

    code = "config"


class HubUnavailableError(MeshError):
    """The hub is not running or cannot be reached."""

    code = "hub_down"


class ProtocolError(MeshError):
    """A frame on the wire is not valid JSON or is too large."""

    code = "protocol"


class NotInSessionError(MeshError):
    """A mesh command was run from a plain terminal instead of from inside an agy session."""

    code = ERR_NOT_IN_SESSION
