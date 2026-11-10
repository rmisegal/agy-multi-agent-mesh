# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Plain data objects exchanged between the hub, the clients and the SDK."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from .constants import KIND_TASK
from .errors import MeshError


def new_id() -> str:
    """Short unique message id (correlates a reply with its request)."""
    return uuid.uuid4().hex[:12]


class DictMixin:
    """Round-trip a dataclass through a JSON-safe dict, ignoring unknown keys."""

    def to_dict(self) -> dict:
        return asdict(self)  # type: ignore[call-overload]

    @classmethod
    def from_dict(cls, data: dict):
        names = {f.name for f in fields(cls)}  # type: ignore[arg-type]
        return cls(**{k: v for k, v in (data or {}).items() if k in names})


@dataclass
class Message(DictMixin):
    """One envelope on the mesh. ``reply_to`` links a reply to the id of its request."""

    sender: str
    to: str
    content: str
    kind: str = KIND_TASK
    reply_to: str | None = None
    origin: dict = field(default_factory=dict)
    id: str = field(default_factory=new_id)
    created: float = field(default_factory=time.time)

    def age(self, now: float | None = None) -> float:
        return (now if now is not None else time.time()) - self.created


@dataclass
class SessionInfo(DictMixin):
    """A joined agy session, the analog of Claude's ``~/.claude/sessions/<pid>.json``."""

    name: str
    role: str = ""
    agy_pid: int | None = None
    cwd: str = ""
    joined: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    state: str = "busy"


@dataclass(frozen=True)
class AgentSpec:
    """One agent of a team: its folder, role and the template used by ``dispatch-all``."""

    name: str
    folder: Path
    role: str = ""
    instructions: str = ""
    task_template: str = "{topic}"

    def task_for(self, topic: str) -> str:
        return self.task_template.replace("{topic}", topic)


@dataclass(frozen=True)
class TeamSpec:
    """A whole team: one master plus any number of worker agents."""

    name: str
    root: Path
    master: AgentSpec
    agents: tuple[AgentSpec, ...]

    @property
    def names(self) -> list[str]:
        return [a.name for a in self.agents]

    def agent(self, name: str) -> AgentSpec:
        for spec in (self.master, *self.agents):
            if spec.name == name:
                return spec
        raise MeshError(f"'{name}' is not part of team '{self.name}' (members: {self.names})")
