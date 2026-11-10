# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""CLI end-to-end against a live hub, with the in-session check satisfied by a fake guard."""

from __future__ import annotations

import threading

import pytest

from agymesh.cli.handlers import parse_tasks
from agymesh.cli.main import main
from agymesh.errors import MeshError
from agymesh.version import __version__

pytestmark = pytest.mark.slow


def run(mesh, capsys, *argv) -> tuple[int, str]:
    code = main(list(argv), mesh=mesh)
    out = capsys.readouterr()
    return code, out.out + out.err


def echo_worker(mesh, name, stop):
    mesh.join(name)
    while not stop.is_set():
        msg = mesh.wait(name, 0.2)
        if msg:
            mesh.reply(name, msg.id, text="PONG " + name if msg.kind == "ping" else "done")


@pytest.fixture
def poem(mesh_factory):
    stop = threading.Event()
    t = threading.Thread(target=echo_worker, args=(mesh_factory(11), "poem", stop), daemon=True)
    t.start()
    master = mesh_factory(10)
    while not master.peers():
        threading.Event().wait(0.05)
    yield master
    stop.set()
    t.join(3)


def test_session_commands(mesh_factory, capsys, tmp_path):
    mesh = mesh_factory(12)
    assert "JOINED as 'joke'" in run(mesh, capsys, "join", "--name", "joke")[1]
    assert "NO_MESSAGE" in run(mesh, capsys, "wait", "--name", "joke", "--timeout", "0")[1]
    answer = tmp_path / "answer.md"
    answer.write_text("hi", encoding="utf-8")
    assert "REPLIED" in run(mesh, capsys, "reply", "--name", "joke", "--id", "x",
                            "--file", str(answer))[1]
    assert run(mesh, capsys, "reply", "--name", "joke", "--id", "x")[0] == 2
    assert "Left the mesh" in run(mesh, capsys, "leave", "--name", "joke")[1]


def test_orchestration_commands(poem, capsys):
    assert "| poem |" in run(poem, capsys, "peers")[1]
    assert f"Hub version {__version__}" in run(poem, capsys, "status")[1]
    assert "PONG poem" in run(poem, capsys, "ping-all", "--name", "master")[1]
    code, out = run(poem, capsys, "dispatch-all", "--topic", "rain", "--timeout", "5")
    assert code == 3 and "Missing parts: art, joke" in out
    code, out = run(poem, capsys, "dispatch", "--to", "poem=rain", "--timeout", "5")
    assert code == 0 and "done" in out
    assert run(poem, capsys, "send", "--to", "poem", "--text", "x", "--timeout", "5")[0] == 0
    assert "Full mesh: all 2 links work" in run(poem, capsys, "mesh-check", "--name", "master")[1]
    assert "Sent PING to nobody" in run(poem, capsys, "ping-all", "--name", "poem",
                                        "--reply-to", "abc")[1]
    out = run(poem, capsys, "dispatch", "--to", "poem=rain", "--timeout", "5")[1]
    assert "SUMMARY FOR THE USER (English only): answered: poem" in out


def test_admin_commands(mesh_factory, capsys, monkeypatch):
    mesh = mesh_factory()
    assert "wrote" in run(mesh, capsys, "init")[1]
    out = run(mesh, capsys, "terminals")[1]
    assert "| agy pid |" in out or "No agy process" in out
    monkeypatch.setattr(type(mesh), "launch", lambda self, *a, **k: ["art"])
    assert "Opened agy windows for: art" in run(mesh, capsys, "launch", "art")[1]
    out = run(mesh, capsys, "up")[1]
    assert "Hub was already running" in out and "Opened agy windows" in out
    assert "Hub is stopping" in run(mesh, capsys, "down")[1]


def test_errors_print_plain_message_and_exit_2(mesh_factory, capsys):
    code, out = run(mesh_factory(None), capsys, "--allow-external", "dispatch", "--to", "bad")
    assert code == 2 and "PEER=TASK" in out


def test_parse_tasks():
    assert parse_tasks(["a=x=y", " b = z "]) == {"a": "x=y", "b": "z"}
    with pytest.raises(MeshError):
        parse_tasks(["=x"])


def test_wait_peers_command(poem, capsys, monkeypatch):
    assert "All 1 workers joined the mesh: poem." in run(poem, capsys, "wait-peers", "--count",
                                                          "1", "--timeout", "1")[1]
    code, out = run(poem, capsys, "wait-peers", "--timeout", "0")
    assert code == 3 and "Only 1 of 3 workers joined" in out
    monkeypatch.setattr(type(poem), "launch", lambda self, *a, **k: ["master"])
    assert "Opened agy windows for: master" in run(poem, capsys, "launch", "--master-only",
                                                   "--ping-test")[1]
