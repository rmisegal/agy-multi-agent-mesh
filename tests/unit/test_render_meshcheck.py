# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Renderer text, ResultWriter files and MeshChecker logic with a fake orchestrator."""

from __future__ import annotations

import json

from agymesh.meshcheck import MeshChecker, MeshReport, parse_sent
from agymesh.models import Message
from agymesh.orchestrate import Reply
from agymesh.render import Renderer
from agymesh.results import ResultWriter, slug

R = Renderer("CMD")


def reply(peer, text="ok", pid=7):
    req = Message("m", peer, "q", created=100.0)
    return Reply(peer, Message(peer, "m", text, kind="reply", origin={"agy_pid": pid},
                               created=101.5), "", req)


class TestRenderer:
    def test_wait_block_per_kind(self):
        assert R.wait_block("poem", None, 3).startswith("NO_MESSAGE")
        ping = R.wait_block("poem", Message("m", "poem", "PING", kind="ping", id="i1"), 0)
        assert 'reply --name poem --id i1 --text "PONG poem"' in ping
        check = R.wait_block("poem", Message("m", "poem", "{}", kind="meshcheck", id="i2"), 0)
        assert "ping-all --name poem --reply-to i2" in check
        task = R.wait_block("poem", Message("m", "poem", "rain", origin={"agy_pid": 9}, id="i3"),
                            0)
        assert "--file answer.md" in task and "agy session pid 9" in task and "rain" in task

    def test_ping_table_and_verdicts(self):
        assert "Nobody to ping" in R.ping_table({})
        good = R.ping_table({"a": reply("a")})
        assert "answered in 1.5s" in good and "All 1 peers answered" in good
        bad = R.ping_table({"a": reply("a"), "b": Reply("b", error="timeout")})
        assert "NO ANSWER" in bad and "1 of 2" in bad

    def test_synthesis_and_summary_line(self):
        res = {"a": reply("a", "x" * 100), "b": Reply("b", error="gone")}
        text = R.synthesis("t", res)
        assert "[A]" in text and "[no answer: gone]" in text and "Missing parts: b" in text
        assert "Every peer delivered" in R.synthesis("t", {"a": reply("a")})
        line = R.result_saved(res, "r.html")
        assert "answered: a; missing: b" in line and "r.html" in line

    def test_tables(self):
        assert "No session has joined" in R.peers_table([])
        assert "| poem | listening | external |" in R.peers_table(
            [{"name": "poem", "state": "listening"}])
        assert "No agy process" in R.terminals_table([])
        assert "| 5 | pwsh (4) | - | not joined |" in R.terminals_table(
            [{"agy_pid": 5, "shell": "pwsh", "shell_pid": 4, "mesh_name": "",
              "state": "not joined"}])

    def test_reply_external_origin_is_flagged(self):
        assert "external terminal" in reply("a", pid=None).answered_by
        assert Reply("a").answered_by == "" and Reply("a").elapsed_s is None


class TestResultWriter:
    def test_writes_markdown_and_rtl_aware_html_and_opens_it(self, tmp_path):
        opened = []
        writer = ResultWriter(tmp_path, True, opened.append, stamp=lambda: "T")
        page = writer.save("חורף ישראלי", {"poem": reply("poem", "שיר <b>"),
                                          "joke": Reply("joke", error="late")})
        html = page.read_text(encoding="utf-8")
        assert opened == [page] and page.name == "T-חורף-ישראלי.html"
        assert '<div class="ln" dir="auto">שיר &lt;b&gt;</div>' in html
        assert "no answer: late" in html
        assert "_no answer: late_" in page.with_suffix(".md").read_text(encoding="utf-8")

    def test_each_line_gets_its_own_direction_and_fences_are_dropped(self):
        out = ResultWriter.lines_html("```text\n  (שקדיות וריח גשם)\n / / /\n\n```")
        assert out.count('dir="auto"') == 3 and "```" not in out and "text" not in out
        assert '<div class="ln" dir="auto">  (שקדיות וריח גשם)</div>' in out
        assert "&nbsp;" in out

    def test_no_open_and_slug_fallback(self, tmp_path):
        opened = []
        ResultWriter(tmp_path, False, opened.append).save("!!", {"a": reply("a")})
        assert opened == [] and slug("!!") == "result"


class FakeOrch:
    me = "master"
    ping_timeout_s = 1

    def __init__(self, dead=(), silent=()):
        self.dead, self.silent = set(dead), set(silent)
        self.asked = []

    def ping_all(self, peers):
        return {p: Reply(p, error="x") if p in self.dead else reply(p, f"PONG {p}")
                for p in peers}

    def fan_out(self, tasks, kind, timeout):
        self.asked = sorted(tasks)
        return {p: reply(p, json.dumps({"sent": {o: f"{p}>{o}" for o in json.loads(t)["peers"]}}))
                for p, t in tasks.items()}

    def await_ids(self, ids, timeout):
        return {pair: None if pair[1] in self.dead | self.silent else Message(pair[1], "", "PONG")
                for pair in ids}


class TestMeshChecker:
    def test_full_mesh_asks_all_peers_at_once(self):
        orch = FakeOrch()
        rep = MeshChecker(orch).run(["a", "b", "c"])
        assert rep.broken == [] and rep.total == 12 and orch.asked == ["a", "b", "c"]
        assert "Full mesh" in R.mesh_report(rep)

    def test_dead_peer_breaks_its_links_and_is_not_asked(self):
        orch = FakeOrch(dead={"b"})
        rep = MeshChecker(orch).run(["a", "b"])
        assert orch.asked == ["a"]
        assert set(rep.broken) == {("master", "b"), ("b", "master"), ("a", "b"), ("b", "a")}
        assert "Not a full mesh" in R.mesh_report(rep)

    def test_silent_pong_is_a_broken_link(self):
        rep = MeshChecker(FakeOrch(silent={"c"})).run(["a", "c"])
        assert set(rep.broken) == {("a", "c")}

    def test_single_peer_and_parse(self):
        assert MeshChecker(FakeOrch()).run(["a"]).total == 2
        assert parse_sent("not json") == {} and parse_sent('{"sent": [1]}') == {}
        assert parse_sent('{"sent": {"a": 1}}') == {"a": "1"}
        assert MeshReport(["x"]).total == 0
