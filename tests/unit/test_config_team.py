# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""MeshConfig, TeamLoader and the models they produce."""

from __future__ import annotations

import json
import os

import pytest

from agymesh.config import MeshConfig, check_version, read_json
from agymesh.errors import ConfigError, MeshError
from agymesh.models import AgentSpec, Message, SessionInfo
from agymesh.team import TeamLoader
from tests.conftest import REAL_TEAM


class TestMeshConfig:
    def test_load_merges_rate_limits_and_reads_dotted_keys(self, config_dir):
        cfg = MeshConfig.load(config_dir)
        assert cfg.get("hub.host") == "127.0.0.1"
        assert cfg.get("rate_limits.messages.max_retries") == 3
        assert cfg.get("missing.key", "dflt") == "dflt"
        assert cfg.get("hub.host.deeper", 7) == 7

    def test_env_overrides_host_port_and_team(self, config_dir, monkeypatch):
        monkeypatch.setenv("AGYMESH_HOST", "127.0.0.2")
        monkeypatch.setenv("AGYMESH_PORT", "1234")
        monkeypatch.setenv("AGYMESH_TEAM", "other.json")
        cfg = MeshConfig.load(config_dir)
        assert (cfg.get("hub.host"), cfg.get("hub.port"), cfg.get("team_file")) == (
            "127.0.0.2", 1234, "other.json")

    def test_wrong_version_is_rejected(self, tmp_path):
        with pytest.raises(ConfigError, match="supported"):
            check_version({"version": "9.99"}, "setup.json")

    def test_missing_and_invalid_files_name_the_path(self, tmp_path):
        with pytest.raises(ConfigError, match="not found"):
            read_json(tmp_path / "nope.json")
        bad = tmp_path / "bad.json"
        bad.write_text("{oops", encoding="utf-8")
        with pytest.raises(ConfigError, match="not valid JSON"):
            read_json(bad)

    def test_resolve_and_command_prefix(self, tmp_path, monkeypatch):
        monkeypatch.setattr("agymesh.config.shutil.which", lambda _name: None)
        cfg = MeshConfig({"command_prefix": ""}, tmp_path)
        assert cfg.resolve("a/b") == (tmp_path / "a" / "b").resolve()
        assert cfg.resolve(tmp_path) == tmp_path
        assert cfg.command_prefix().startswith('uv run --project "')
        assert MeshConfig({"command_prefix": "agymesh"}, tmp_path).command_prefix() == "agymesh"

    def test_command_prefix_prefers_project_venv_launcher(self, tmp_path, monkeypatch):
        monkeypatch.setattr("agymesh.config.os.name", "nt")
        for root in (tmp_path / "plain", tmp_path / "with space"):
            exe = root / ".venv" / "Scripts" / "agymesh.exe"
            exe.parent.mkdir(parents=True)
            exe.write_bytes(b"")
            prefix = MeshConfig({}, root).command_prefix()
            assert prefix == (f'& "{exe}"' if " " in str(root) else str(exe))

    def test_command_prefix_uses_agymesh_on_path_without_venv(self, tmp_path, monkeypatch):
        found = {"agymesh": r"C:\shared\bin\agymesh.cmd"}
        monkeypatch.setattr("agymesh.config.shutil.which", found.get)
        assert MeshConfig({}, tmp_path).command_prefix() == "agymesh"
        scripts = tmp_path / ".venv" / ("Scripts" if os.name == "nt" else "bin")
        scripts.mkdir(parents=True)
        (scripts / ("agymesh.exe" if os.name == "nt" else "agymesh")).write_bytes(b"")
        assert MeshConfig({}, tmp_path).command_prefix() != "agymesh"  # the project venv still wins


class TestTeamLoader:
    def test_real_example_team_loads(self):
        team = TeamLoader().load(REAL_TEAM)
        assert team.names == ["art", "poem", "joke"]
        assert team.master.name == "master"
        assert team.agent("poem").folder.name == "poem"
        assert "חורף" in team.agent("poem").task_for("חורף")

    def _write(self, tmp_path, data) -> str:
        path = tmp_path / "t.json"
        path.write_text(json.dumps({"version": "1.00", **data}), encoding="utf-8")
        return str(path)

    def test_errors(self, tmp_path):
        loader = TeamLoader()
        with pytest.raises(ConfigError, match="defines no agents"):
            loader.load(self._write(tmp_path, {"agents": []}))
        with pytest.raises(ConfigError, match="invalid"):
            loader.load(self._write(tmp_path, {"agents": [{"name": "Bad Name"}]}))
        with pytest.raises(ConfigError, match="repeats"):
            loader.load(self._write(tmp_path, {"agents": [{"name": "a"}, {"name": "a"}]}))

    def test_unknown_member(self):
        with pytest.raises(MeshError, match="not part of team"):
            TeamLoader().load(REAL_TEAM).agent("ghost")


class TestModels:
    def test_message_round_trip_ignores_unknown_keys(self):
        msg = Message("a", "b", "hi")
        again = Message.from_dict({**msg.to_dict(), "extra": 1})
        assert again == msg
        assert msg.age(msg.created + 2) == pytest.approx(2)

    def test_session_info_and_agent_template(self, tmp_path):
        info = SessionInfo.from_dict({"name": "x", "agy_pid": 5, "unknown": True})
        assert (info.name, info.agy_pid) == ("x", 5)
        assert AgentSpec("a", tmp_path, task_template="T:{topic}").task_for("z") == "T:z"
