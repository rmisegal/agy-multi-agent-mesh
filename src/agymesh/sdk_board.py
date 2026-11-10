# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""BoardMixin: the shared TODO board through the SDK (writes are in-session only)."""

from __future__ import annotations

from .constants import OP_BOARD_ADD, OP_BOARD_CLAIM, OP_BOARD_CLEAR, OP_BOARD_DONE, OP_BOARD_LIST


class BoardMixin:
    """``todo_*`` methods; add/claim/done are stamped by the OriginGuard like every message."""

    def todo_add(self, name: str, titles: list[str]) -> list[dict]:
        self.guard.stamp()
        return self.client.request({"op": OP_BOARD_ADD, "by": name, "titles": titles})["tasks"]

    def todo_claim(self, name: str, task_id: str | None = None) -> dict | None:
        self.guard.stamp()
        return self.client.request({"op": OP_BOARD_CLAIM, "by": name, "id": task_id})["task"]

    def todo_done(self, name: str, task_id: str, note: str = "") -> dict:
        self.guard.stamp()
        return self.client.request({"op": OP_BOARD_DONE, "by": name, "id": task_id,
                                    "note": note})["task"]

    def todo_list(self, status: str | None = None) -> list[dict]:
        return self.client.request({"op": OP_BOARD_LIST, "status": status})["tasks"]

    def todo_clear(self) -> int:
        return self.client.request({"op": OP_BOARD_CLEAR})["removed"]
