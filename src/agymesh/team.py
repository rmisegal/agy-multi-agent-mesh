# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""TeamLoader: read a team file (master + workers) into a validated TeamSpec."""

from __future__ import annotations

import re
from pathlib import Path

from .config import check_version, read_json
from .errors import ConfigError
from .models import AgentSpec, TeamSpec

NAME_RE = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")


class TeamLoader:
    """Folders in a team file are relative to the team file's own directory."""

    def load(self, path: str | Path) -> TeamSpec:
        path = Path(path).resolve()
        data = read_json(path)
        check_version(data, path.name)
        root = path.parent
        master = self._agent(data.get("master") or {"name": "master", "folder": "master"}, root)
        agents = tuple(self._agent(raw, root) for raw in data.get("agents") or [])
        if not agents:
            raise ConfigError(f"team file {path} defines no agents")
        names = [master.name, *(a.name for a in agents)]
        if len(set(names)) != len(names):
            raise ConfigError(f"team file {path} repeats an agent name: {names}")
        return TeamSpec(name=data.get("name", path.stem), root=root, master=master, agents=agents)

    @staticmethod
    def _agent(raw: dict, root: Path) -> AgentSpec:
        name = str(raw.get("name", ""))
        if not NAME_RE.match(name):
            raise ConfigError(
                f"agent name '{name}' is invalid: use lowercase letters, digits, - or _"
            )
        folder = Path(raw.get("folder") or name)
        return AgentSpec(
            name=name,
            folder=folder if folder.is_absolute() else (root / folder).resolve(),
            role=raw.get("role", ""),
            instructions=raw.get("instructions", ""),
            task_template=raw.get("task_template", "{topic}"),
        )
