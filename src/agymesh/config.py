# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""MeshConfig: versioned settings from ``config/setup.json`` + ``config/rate_limits.json``.

Environment variables (see ``.env-example``) override the host, port, config folder and team.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .constants import ENV_CONFIG_DIR, ENV_HOST, ENV_PORT, ENV_TEAM
from .errors import ConfigError
from .version import SUPPORTED_CONFIG_VERSIONS

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def read_json(path: Path) -> dict:
    """Read a JSON file (BOM tolerant) and raise ConfigError with the path when it fails."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except ValueError as exc:
        raise ConfigError(f"config file is not valid JSON: {path} ({exc})") from exc


def check_version(data: dict, where: str) -> None:
    version = str(data.get("version", "unknown"))
    if version not in SUPPORTED_CONFIG_VERSIONS:
        raise ConfigError(
            f"{where} has version {version}; supported: {list(SUPPORTED_CONFIG_VERSIONS)}"
        )


class MeshConfig:
    """Dotted-key access to the merged settings, with defaults as the only fallback."""

    def __init__(self, data: dict, root: Path) -> None:
        self.data = data
        self.root = Path(root)

    @classmethod
    def load(cls, config_dir: str | Path | None = None) -> MeshConfig:
        cdir = Path(config_dir or os.environ.get(ENV_CONFIG_DIR) or DEFAULT_CONFIG_DIR).resolve()
        setup = read_json(cdir / "setup.json")
        check_version(setup, "setup.json")
        rates_file = cdir / "rate_limits.json"
        rates = read_json(rates_file).get("rate_limits", {}) if rates_file.exists() else {}
        if rates:
            check_version(rates, "rate_limits.json")
        data = {**setup, "rate_limits": rates}
        cls._apply_env(data)
        return cls(data, cdir.parent)

    @staticmethod
    def _apply_env(data: dict) -> None:
        hub = data.setdefault("hub", {})
        if os.environ.get(ENV_HOST):
            hub["host"] = os.environ[ENV_HOST]
        if os.environ.get(ENV_PORT):
            hub["port"] = int(os.environ[ENV_PORT])
        if os.environ.get(ENV_TEAM):
            data["team_file"] = os.environ[ENV_TEAM]

    def get(self, dotted: str, default=None):
        node = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def resolve(self, path: str | Path) -> Path:
        """Resolve a path from the config relative to the project root."""
        p = Path(path)
        return p if p.is_absolute() else (self.root / p).resolve()

    def command_prefix(self) -> str:
        """How an agy session invokes the CLI.

        Auto: the project's own ``.venv`` launcher (no ``uv`` sync check on every ``wait``),
        falling back to ``uv run --project <root> agymesh`` before ``uv sync`` has run.
        """
        custom = self.get("command_prefix", "")
        if custom:
            return custom
        scripts = "Scripts" if os.name == "nt" else "bin"
        suffix = ".exe" if os.name == "nt" else ""
        exe = self.root / ".venv" / scripts / f"agymesh{suffix}"
        if exe.exists():
            return f'& "{exe}"' if " " in str(exe) else str(exe)
        return f'uv run --project "{self.root}" agymesh'
