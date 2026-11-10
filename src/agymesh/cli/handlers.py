# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""One small handler per sub-command: call the SDK, render, return an exit code."""

from __future__ import annotations

import argparse
import time

from ..errors import MeshError
from ..render import Renderer
from ..sdk import AgyMesh


def parse_tasks(items: list[str]) -> dict[str, str]:
    tasks: dict[str, str] = {}
    for item in items:
        peer, sep, task = item.partition("=")
        if not sep or not peer.strip() or not task.strip():
            raise MeshError(f"--to must look like PEER=TASK, got: {item!r}")
        tasks[peer.strip()] = task.strip()
    return tasks


class Handlers:
    def __init__(self, mesh: AgyMesh, out=print) -> None:
        self.mesh = mesh
        self.out = out
        self.render = Renderer(mesh.config.command_prefix(),
                               mesh.config.get("session.answer_file", "answer.md"))

    def run(self, args: argparse.Namespace) -> int:
        handler = getattr(self, "cmd_" + args.command.replace("-", "_"))
        return int(handler(args) or 0)

    def cmd_hub(self, args) -> int:
        self.mesh.serve_hub(on_ready=lambda host, port: self.out(
            f"Hub is running on {host}:{port}. Leave this window open; Ctrl+C stops it."))
        self.out("Hub stopped.")

    def cmd_up(self, args) -> int:
        res = self.mesh.up(launch=not args.no_launch, with_master=args.with_master)
        self.out("Hub started in the background." if res["hub_started"]
                 else "Hub was already running - reusing it.")
        self.out("Wrote instructions:\n  " + "\n  ".join(res["instructions"]))
        if res["opened"]:
            self.out("Opened agy windows for: " + ", ".join(res["opened"]) +
                     ". Each one joins the mesh and starts listening by itself.")

    def cmd_down(self, args) -> int:
        self.out("Hub is stopping." if self.mesh.hub_down() else "Hub was not running.")

    def cmd_status(self, args) -> int:
        st = self.mesh.status()
        self.out(f"Hub version {st['version']} is running. Waiting messages: "
                 f"{st['queued'] or 'none'}; dropped: {st['dropped']}.")
        self.out(self.render.peers_table(st["sessions"]))

    def cmd_init(self, args) -> int:
        for path in self.mesh.write_instructions():
            self.out(f"wrote {path}")

    def cmd_launch(self, args) -> int:
        opened = self.mesh.launch(args.agents or None, args.with_master)
        self.out("Opened agy windows for: " + ", ".join(opened))

    def cmd_peers(self, args) -> int:
        self.out(self.render.peers_table(self.mesh.peers()))

    def cmd_terminals(self, args) -> int:
        self.out(self.render.terminals_table(self.mesh.terminals()))

    def cmd_join(self, args) -> int:
        res = self.mesh.join(args.name, args.role)
        others = [p for p in res["peers"] if p != args.name]
        self.out(f"JOINED as '{args.name}'. Other sessions online: {', '.join(others) or 'none yet'}."
                 f"\nNEXT: {self.render.cmd} wait --name {args.name}")

    def cmd_leave(self, args) -> int:
        self.out("Left the mesh." if self.mesh.leave(args.name) else "Was not joined.")

    def cmd_wait(self, args) -> int:
        start = time.monotonic()
        msg = self.mesh.wait(args.name, args.timeout)
        self.out(self.render.wait_block(args.name, msg, time.monotonic() - start))

    def cmd_reply(self, args) -> int:
        self.mesh.reply(args.name, args.id, args.text, args.file)
        self.out(f"REPLIED to {args.id}.\nNEXT: {self.render.cmd} wait --name {args.name}")

    def _deliver(self, title: str, results: dict) -> int:
        self.out(self.render.synthesis(title, results))
        page = self.mesh.save_result(title, results)
        self.out(self.render.result_saved(results, page))
        return 0 if all(r.ok for r in results.values()) else 3

    def cmd_send(self, args) -> int:
        r = self.mesh.send(args.to, args.text, args.name, args.timeout)
        return self._deliver(f"reply from {args.to}", {args.to: r})

    def cmd_dispatch(self, args) -> int:
        results = self.mesh.dispatch(parse_tasks(args.to), args.name, args.timeout)
        return self._deliver("custom dispatch", results)

    def cmd_dispatch_all(self, args) -> int:
        return self._deliver(args.topic,
                             self.mesh.dispatch_all(args.topic, args.name, args.timeout))

    def cmd_ping_all(self, args) -> int:
        if args.reply_to:
            sent = self.mesh.relay_pings(args.name, args.reply_to, args.exclude)
            self.out(f"Sent PING to {', '.join(sent) or 'nobody'} and told the requester the "
                     "message ids; it collects the PONGs itself.\n"
                     f"NEXT: {self.render.cmd} wait --name {args.name}")
            return 0
        self.out(self.render.ping_table(self.mesh.ping_all(args.name, args.exclude)))

    def cmd_todo_add(self, args) -> int:
        tasks = self.mesh.todo_add(args.name, args.title)
        self.out("ADDED " + ", ".join(f"{t['id']} ({t['title']})" for t in tasks))

    def cmd_todo_claim(self, args) -> int:
        self.out(self.render.claimed(args.name, self.mesh.todo_claim(args.name, args.id)))

    def cmd_todo_done(self, args) -> int:
        task = self.mesh.todo_done(args.name, args.id, args.note)
        self.out(f"DONE {task['id']}.\nNEXT: {self.render.cmd} todo-claim --name {args.name}")

    def cmd_todo_list(self, args) -> int:
        self.out(self.render.board_table(self.mesh.todo_list(args.status)))

    def cmd_todo_clear(self, args) -> int:
        self.out(f"Removed {self.mesh.todo_clear()} task(s) from the board.")

    def cmd_mesh_check(self, args) -> int:
        self.out(self.render.mesh_report(self.mesh.mesh_check(args.name)))
