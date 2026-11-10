# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Renderer: turns SDK results into plain-language terminal text (no bare status tokens)."""

from __future__ import annotations

from .constants import KIND_MESHCHECK, KIND_PING
from .meshcheck import MeshReport
from .models import Message
from .orchestrate import Reply

RULE = "=" * 60


class Renderer:
    def __init__(self, cmd: str, answer_file: str = "answer.md") -> None:
        self.cmd = cmd
        self.answer_file = answer_file

    def wait_block(self, name: str, msg: Message | None, waited_s: float) -> str:
        again = f"{self.cmd} wait --name {name}"
        if msg is None:
            return (f"NO_MESSAGE - nothing arrived in {waited_s:.0f}s. That is normal.\n"
                    f"NEXT: run the same command again now: {again}")
        sender = msg.origin.get("agy_pid")
        via = f"agy session pid {sender}" if sender else "an external terminal"
        if msg.kind == KIND_PING:
            nxt = f'{self.cmd} reply --name {name} --id {msg.id} --text "PONG {name}"'
        elif msg.kind == KIND_MESHCHECK:
            nxt = f"{self.cmd} ping-all --name {name} --reply-to {msg.id}"
        else:
            nxt = (f"do the task as your role says, write the full answer to "
                   f"{self.answer_file}, then run:\n  "
                   f"{self.cmd} reply --name {name} --id {msg.id} --file {self.answer_file}")
        return (f"MESSAGE id={msg.id} kind={msg.kind} from={msg.sender} (sent by {via})\n"
                f"----- content -----\n{msg.content}\n----- end -----\n"
                f"NEXT: {nxt}\nAFTER THAT: {again}")

    @staticmethod
    def reply_line(peer: str, r: Reply) -> str:
        if r.ok:
            return f"| {peer} | answered in {r.elapsed_s}s | {r.answered_by} | {_one_line(r.text)} |"
        return f"| {peer} | NO ANSWER | - | {r.error} |"

    def ping_table(self, results: dict[str, Reply]) -> str:
        if not results:
            return "Nobody to ping: no other session has joined the mesh yet."
        rows = ["| Peer | Result | Answered by | Reply / reason |", "|---|---|---|---|"]
        rows += [self.reply_line(p, r) for p, r in results.items()]
        ok = sum(r.ok for r in results.values())
        verdict = (f"All {ok} peers answered from their own agy sessions." if ok == len(results)
                   else f"{ok} of {len(results)} peers answered. A peer with NO ANSWER is busy "
                        "on a long task, waiting on a permission prompt, or not in its wait loop.")
        return "\n".join([*rows, "", verdict])

    def synthesis(self, title: str, results: dict[str, Reply]) -> str:
        parts = [RULE, f"  UNIFIED MESH RESULT: {title}", RULE]
        for peer, r in results.items():
            parts.append(f"\n--- [{peer.upper()}] ({r.answered_by or 'no answer'}) ---")
            parts.append(r.text if r.ok else f"[no answer: {r.error}]")
        missing = [p for p, r in results.items() if not r.ok]
        parts.append("\n" + (f"Missing parts: {', '.join(missing)}." if missing
                             else "Every peer delivered its part."))
        return "\n".join(parts)

    @staticmethod
    def result_saved(results: dict[str, Reply], page) -> str:
        ok = [p for p, r in results.items() if r.ok]
        missing = [p for p, r in results.items() if not r.ok]
        gaps = f"; missing: {', '.join(missing)}" if missing else ""
        return (f"RESULT FILE: {page} (opened in the browser - Hebrew reads correctly there)\n"
                f"SUMMARY FOR THE USER (English only): answered: {', '.join(ok) or 'nobody'}"
                f"{gaps}; result opened in the browser: {page}")

    def claimed(self, name: str, task: dict | None) -> str:
        if task is None:
            return "NO_OPEN_TASK - the board has no open task left. Reply to whoever asked you."
        return (f"CLAIMED {task['id']}: {task['title']}\nNEXT: do it, then run: {self.cmd} "
                f'todo-done --name {name} --id {task["id"]} --note "<one-line result>"')

    @staticmethod
    def board_table(rows: list[dict]) -> str:
        if not rows:
            return "The shared TODO board is empty."
        out = ["| ID | Status | Owner | Task | Note |", "|---|---|---|---|---|"]
        out += [f"| {t['id']} | {t['status']} | {t['owner'] or '-'} | {t['title']} | "
                f"{t['note'] or ''} |" for t in rows]
        left = sum(t["status"] != "done" for t in rows)
        return "\n".join([*out, "", f"{len(rows) - left} of {len(rows)} done, {left} left."])

    @staticmethod
    def peers_table(rows: list[dict]) -> str:
        if not rows:
            return "No session has joined the mesh yet. Start the agents with `agymesh up`."
        out = ["| Name | State | agy pid | Idle (s) | Folder |", "|---|---|---|---|---|"]
        out += [f"| {r['name']} | {r['state']} | {r.get('agy_pid') or 'external'} | "
                f"{r.get('idle_s', '')} | {r.get('cwd', '')} |" for r in rows]
        return "\n".join(out)

    @staticmethod
    def terminals_table(rows: list[dict]) -> str:
        if not rows:
            return "No agy process is running on this PC."
        out = ["| agy pid | Shell (pid) | Mesh name | State |", "|---|---|---|---|"]
        out += [f"| {r['agy_pid']} | {r['shell']} ({r['shell_pid']}) | "
                f"{r['mesh_name'] or '-'} | {r['state']} |" for r in rows]
        return "\n".join(out)

    @staticmethod
    def mesh_report(rep: MeshReport) -> str:
        names = rep.names
        legend = [f"#{i} = {n}" for i, n in enumerate(names, 1)]
        head = "| | " + " | ".join(f"#{i}" for i in range(1, len(names) + 1)) + " |"
        rows = [head, "|---" * (len(names) + 1) + "|"]
        for i, a in enumerate(names, 1):
            cells = ["-" if a == b else ("OK" if rep.links.get((a, b)) else "FAIL")
                     for b in names]
            rows.append(f"| **#{i}** | " + " | ".join(cells) + " |")
        bad = rep.broken
        verdict = (f"Full mesh: all {rep.total} links work." if not bad else
                   f"Not a full mesh: {rep.total - len(bad)} of {rep.total} links work. "
                   "Broken: " + ", ".join(f"{a}->{b}" for a, b in bad))
        return "\n".join([verdict, "", *legend, "",
                          "Row sent PING, column answered PONG:", *rows])


def _one_line(text: str, limit: int = 60) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."
