# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Argument parser for the ``agymesh`` command."""

from __future__ import annotations

import argparse

from ..version import COPYRIGHT, __version__


def _name(p: argparse.ArgumentParser, required: bool = True) -> None:
    p.add_argument("--name", required=required, help="this session's mesh name")


def _board(sub) -> None:
    """The shared TODO board (one list for the whole team, kept by the hub)."""
    add = sub.add_parser("todo-add", help="[in session] add one or more tasks to the board")
    _name(add)
    add.add_argument("--title", action="append", required=True, help="repeat for many tasks")
    claim = sub.add_parser("todo-claim", help="[in session] take the next open task (atomic)")
    _name(claim)
    claim.add_argument("--id", default=None, help="a specific task instead of the next one")
    done = sub.add_parser("todo-done", help="[in session] mark your task done")
    _name(done)
    done.add_argument("--id", required=True)
    done.add_argument("--note", default="", help="one-line result or where the output is")
    lst = sub.add_parser("todo-list", help="show the board")
    lst.add_argument("--status", choices=["open", "claimed", "done"], default=None)
    sub.add_parser("todo-clear", help="remove every task from the board")


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="agymesh", description=(
        "Session-to-session messaging for Antigravity CLI (agy). Mesh commands must be run BY "
        "an agy session (its shell tool); setup commands (up/down/hub/init) run anywhere."))
    root.add_argument("--version", action="version", version=f"agymesh {__version__} - {COPYRIGHT}")
    root.add_argument("--config-dir", help="folder with setup.json and rate_limits.json")
    root.add_argument("--team", help="team file (default: team_file in setup.json)")
    root.add_argument("--allow-external", action="store_true",
                      help="diagnostics only: allow mesh commands from a plain terminal")
    sub = root.add_subparsers(dest="command", required=True)

    sub.add_parser("hub", help="run the hub in this window (Ctrl+C stops it)")
    up = sub.add_parser("up", help="start hub, write AGY.md files, open one agy window per agent")
    up.add_argument("--no-launch", action="store_true", help="do not open agy windows")
    up.add_argument("--with-master", action="store_true", help="also open the master window")
    sub.add_parser("down", help="stop the hub")
    sub.add_parser("status", help="hub version, sessions and queue depths")
    sub.add_parser("init", help="(re)write AGY.md for the master and every agent")
    launch = sub.add_parser("launch", help="open agy windows for some or all agents")
    launch.add_argument("agents", nargs="*", help="agent names (default: all)")
    launch.add_argument("--with-master", action="store_true")
    launch.add_argument("--master-only", action="store_true", help="open only the master")
    launch.add_argument("--ping-test", action="store_true",
                        help="the master runs the PING/PONG check right after it boots")
    wp = sub.add_parser("wait-peers", help="wait until the workers have joined the mesh")
    wp.add_argument("--count", type=int, default=None, help="default: every team agent")
    wp.add_argument("--timeout", type=float, default=300.0)
    sub.add_parser("peers", help="sessions that joined the mesh (ListAgents analog)")
    sub.add_parser("terminals", help="running agy processes matched to mesh names")

    join = sub.add_parser("join", help="[in session] register this agy session")
    _name(join)
    join.add_argument("--role", default=None)
    leave = sub.add_parser("leave", help="[in session] unregister")
    _name(leave)
    wait = sub.add_parser("wait", help="[in session] block until a message arrives")
    _name(wait)
    wait.add_argument("--timeout", type=float, default=None, help="seconds (default: config)")
    reply = sub.add_parser("reply", help="[in session] answer a message by its id")
    _name(reply)
    reply.add_argument("--id", required=True, help="id of the message you answer")
    reply.add_argument("--text", default=None)
    reply.add_argument("--file", default=None, help="file holding the full answer")

    send = sub.add_parser("send", help="[in session] send one message and wait for the reply")
    _name(send, required=False)
    send.add_argument("--to", required=True)
    send.add_argument("--text", required=True)
    send.add_argument("--timeout", type=float, default=None)
    disp = sub.add_parser("dispatch", help="[in session] parallel custom sub-tasks")
    _name(disp, required=False)
    disp.add_argument("--to", action="append", required=True, metavar="PEER=TASK")
    disp.add_argument("--timeout", type=float, default=None)
    dall = sub.add_parser("dispatch-all", help="[in session] topic -> every agent's template")
    _name(dall, required=False)
    dall.add_argument("--topic", required=True)
    dall.add_argument("--timeout", type=float, default=None)
    ping = sub.add_parser("ping-all", help="[in session] PING every joined peer")
    _name(ping, required=False)
    ping.add_argument("--reply-to", default=None, help="send the result as a reply to this id")
    ping.add_argument("--exclude", action="append", default=[])
    check = sub.add_parser("mesh-check", help="[in session] full who-reaches-whom matrix")
    _name(check, required=False)
    _board(sub)
    return root
