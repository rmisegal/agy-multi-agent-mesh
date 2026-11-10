# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""MeshChecker: full who-reached-whom matrix, the analog of cli:mesh-communication's check.

1. The master pings every peer (master -> peer; the PONG travels peer -> master).
2. ALL peers get a ``meshcheck`` request at once. Each agy session runs ``ping-all --reply-to``,
   which only POSTS its PINGs and replies at once with their message ids - it does not wait for
   the PONGs, so it is back in ``wait`` immediately and can answer the other peers' PINGs.
3. The master collects every PONG from the hub's reply book by those ids.

Version 1.00 asked one peer at a time (a peer blocked in its own ping-all could not answer
anyone); measured live it cost ~7 sequential LLM turns. Now the rounds overlap: ~3 turns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .constants import KIND_MESHCHECK
from .orchestrate import Orchestrator


@dataclass
class MeshReport:
    names: list[str]
    links: dict[tuple[str, str], bool] = field(default_factory=dict)
    answered_by: dict[str, str] = field(default_factory=dict)

    @property
    def broken(self) -> list[tuple[str, str]]:
        return [pair for pair, ok in self.links.items() if not ok]

    @property
    def total(self) -> int:
        return len(self.links)


def parse_sent(text: str) -> dict[str, str]:
    """``{"sent": {peer: ping_id}}`` from a peer's meshcheck reply; {} if malformed."""
    try:
        data = json.loads(text)
    except ValueError:
        return {}
    sent = data.get("sent") if isinstance(data, dict) else None
    return {str(k): str(v) for k, v in sent.items()} if isinstance(sent, dict) else {}


class MeshChecker:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orch = orchestrator

    def run(self, peers: list[str]) -> MeshReport:
        me, timeout = self.orch.me, self.orch.ping_timeout_s
        report = MeshReport(names=[me, *peers])
        direct = self.orch.ping_all(peers)
        for peer in peers:
            ok = direct[peer].ok
            report.links[(me, peer)] = report.links[(peer, me)] = ok
            report.answered_by[peer] = direct[peer].answered_by
        pairs = [(a, b) for a in peers for b in peers if a != b]
        report.links.update(dict.fromkeys(pairs, False))
        alive = [p for p in peers if direct[p].ok]
        if len(peers) < 2 or not alive:
            return report
        asks = self.orch.fan_out(
            {p: json.dumps({"peers": [o for o in peers if o != p]}) for p in alive},
            KIND_MESHCHECK, timeout)
        pending = {(p, o): pid for p in alive
                   for o, pid in parse_sent(asks[p].text).items() if (p, o) in report.links}
        for pair, pong in self.orch.await_ids(pending, timeout).items():
            report.links[pair] = pong is not None
        return report
