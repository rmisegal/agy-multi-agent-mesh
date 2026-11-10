# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""TaskBoard: ONE shared TODO list for the whole team, kept by the hub.

Why not a shared TODO file? Several LLM sessions editing one file race: two agents read the same
"open" line, both take it, and the later write overwrites the earlier one. Here every change
goes through the hub under a lock, so ``claim`` is atomic - two agents asking at the same
moment always get two different tasks. The board is saved to JSON after every change, so it
survives a hub restart. (Mailboxes stay private, point-to-point; the board is shared.)
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path

from ..errors import MeshError

ERR_BOARD = "board"
STATUSES = ("open", "claimed", "done")


class TaskBoard:
    def __init__(self, path: Path | None = None, clock: Callable[[], float] = time.time) -> None:
        self.path = Path(path) if path else None
        self.clock = clock
        self._lock = threading.Lock()
        self._tasks: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if not self.path or not self.path.exists():
            return {}
        rows = json.loads(self.path.read_text(encoding="utf-8") or "[]")
        return {row["id"]: row for row in rows}

    def _save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(list(self._tasks.values()), ensure_ascii=False, indent=1),
                       encoding="utf-8")
        os.replace(tmp, self.path)

    def _get(self, task_id: str) -> dict:
        task = self._tasks.get(task_id)
        if task is None:
            raise MeshError(f"no task '{task_id}' on the board", ERR_BOARD)
        return task

    def add(self, title: str, by: str) -> dict:
        if not title.strip():
            raise MeshError("a task needs a title", ERR_BOARD)
        with self._lock:
            task_id = f"T{len(self._tasks) + 1:03d}"
            now = self.clock()
            self._tasks[task_id] = {"id": task_id, "title": title.strip(), "status": "open",
                                    "owner": "", "created_by": by, "note": "",
                                    "created": now, "updated": now}
            self._save()
            return dict(self._tasks[task_id])

    def claim(self, by: str, task_id: str | None = None) -> dict | None:
        """Atomically take a task (the given one, or the oldest open one). None = nothing open."""
        with self._lock:
            if task_id:
                task = self._get(task_id)
                if task["status"] != "open":
                    raise MeshError(f"{task_id} is {task['status']} (owner: {task['owner']})",
                                    ERR_BOARD)
            else:
                task = next((t for t in self._tasks.values() if t["status"] == "open"), None)
                if task is None:
                    return None
            task.update(status="claimed", owner=by, updated=self.clock())
            self._save()
            return dict(task)

    def done(self, task_id: str, by: str, note: str = "") -> dict:
        with self._lock:
            task = self._get(task_id)
            if task["status"] == "claimed" and task["owner"] != by:
                raise MeshError(f"{task_id} is claimed by '{task['owner']}', not '{by}'",
                                ERR_BOARD)
            task.update(status="done", owner=task["owner"] or by, note=note,
                        updated=self.clock())
            self._save()
            return dict(task)

    def rows(self, status: str | None = None) -> list[dict]:
        with self._lock:
            return [dict(t) for t in self._tasks.values() if not status or t["status"] == status]

    def clear(self) -> int:
        with self._lock:
            count = len(self._tasks)
            self._tasks.clear()
            self._save()
            return count
