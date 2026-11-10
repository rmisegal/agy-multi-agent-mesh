# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""BoardOpsMixin: the hub operations of the shared TODO board (add / claim / done / list)."""

from __future__ import annotations

from .. import constants as c
from .board import TaskBoard


class BoardOpsMixin:
    """Needs ``self.board`` (TaskBoard) and ``self.journal``; registers its ops in ``_ops``."""

    board: TaskBoard

    def board_ops(self) -> dict:
        return {c.OP_BOARD_ADD: self._board_add, c.OP_BOARD_CLAIM: self._board_claim,
                c.OP_BOARD_DONE: self._board_done, c.OP_BOARD_LIST: self._board_list,
                c.OP_BOARD_CLEAR: self._board_clear}

    def _board_add(self, req: dict) -> dict:
        tasks = [self.board.add(title, req["by"]) for title in req["titles"]]
        self.journal("board_add", {"by": req["by"], "ids": [t["id"] for t in tasks]})
        return {"tasks": tasks}

    def _board_claim(self, req: dict) -> dict:
        task = self.board.claim(req["by"], req.get("id"))
        self.journal("board_claim", {"by": req["by"], "id": task["id"] if task else None})
        return {"task": task}

    def _board_done(self, req: dict) -> dict:
        task = self.board.done(req["id"], req["by"], req.get("note", ""))
        self.journal("board_done", {"by": req["by"], "id": task["id"]})
        return {"task": task}

    def _board_list(self, req: dict) -> dict:
        return {"tasks": self.board.rows(req.get("status"))}

    def _board_clear(self, req: dict) -> dict:
        return {"removed": self.board.clear()}
