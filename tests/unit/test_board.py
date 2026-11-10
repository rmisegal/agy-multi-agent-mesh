# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Shared TODO board: TaskBoard logic, persistence, atomic claims, hub ops and the CLI."""

from __future__ import annotations

import threading

import pytest

from agymesh.cli.main import main
from agymesh.errors import MeshError
from agymesh.hub.board import TaskBoard


class TestTaskBoard:
    def test_add_claim_done_flow(self):
        board = TaskBoard()
        a, b = board.add("first", "master"), board.add(" second ", "master")
        assert (a["id"], b["id"], b["title"]) == ("T001", "T002", "second")
        assert board.claim("poem")["id"] == "T001"
        assert board.claim("joke", "T002")["owner"] == "joke"
        assert board.claim("art") is None
        assert board.done("T001", "poem", "ok")["status"] == "done"
        assert [t["id"] for t in board.rows("claimed")] == ["T002"]

    def test_errors_are_explained(self):
        board = TaskBoard()
        with pytest.raises(MeshError, match="needs a title"):
            board.add("  ", "m")
        board.add("x", "m")
        board.claim("poem")
        with pytest.raises(MeshError, match="claimed by 'poem'"):
            board.done("T001", "joke")
        with pytest.raises(MeshError, match="is claimed"):
            board.claim("joke", "T001")
        with pytest.raises(MeshError, match="no task 'T009'"):
            board.done("T009", "poem")

    def test_open_task_can_be_closed_directly_and_clear(self):
        board = TaskBoard()
        board.add("x", "m")
        assert board.done("T001", "art")["owner"] == "art"
        assert board.clear() == 1 and board.rows() == []

    def test_survives_a_hub_restart(self, tmp_path):
        path = tmp_path / "b" / "board.json"
        TaskBoard(path).add("שיר על חורף", "master")
        again = TaskBoard(path)
        assert again.rows()[0]["title"] == "שיר על חורף"
        assert again.add("next", "m")["id"] == "T002"

    def test_parallel_claims_never_give_one_task_twice(self):
        board = TaskBoard()
        for i in range(5):
            board.add(f"task {i}", "master")
        got, barrier = [], threading.Barrier(8)

        def agent(n):
            barrier.wait()
            task = board.claim(f"agent{n}")
            if task:
                got.append(task["id"])

        threads = [threading.Thread(target=agent, args=(n,)) for n in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(5)
        assert sorted(got) == ["T001", "T002", "T003", "T004", "T005"]


@pytest.mark.slow
def test_board_through_cli_and_hub(mesh_factory, capsys):
    mesh = mesh_factory()

    def run(*argv):
        code = main(list(argv), mesh=mesh)
        return code, capsys.readouterr().out

    assert "ADDED T001 (rain), T002 (snow)" in run("todo-add", "--name", "master",
                                                   "--title", "rain", "--title", "snow")[1]
    assert "CLAIMED T001: rain" in run("todo-claim", "--name", "poem")[1]
    assert "DONE T001" in run("todo-done", "--name", "poem", "--id", "T001", "--note", "ok")[1]
    out = run("todo-list")[1]
    assert "| T001 | done | poem | rain | ok |" in out and "1 of 2 done, 1 left." in out
    assert "| T002 | open |" in run("todo-list", "--status", "open")[1]
    run("todo-claim", "--name", "joke")
    assert "NO_OPEN_TASK" in run("todo-claim", "--name", "joke")[1]
    assert run("todo-done", "--name", "art", "--id", "T002")[0] == 2
    assert "Removed 2 task(s)" in run("todo-clear")[1]
    assert "board is empty" in run("todo-list")[1]
