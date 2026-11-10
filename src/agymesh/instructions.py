# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""InstructionWriter: render AGY.md for the master and every worker from one team file.

The failed project kept three copies of each AGY.md (in two .ps1 scripts and a .txt) that drifted
apart. Here the team file is the single source; AGY.md is generated, never edited by hand.
"""

from __future__ import annotations

from pathlib import Path

from .constants import INSTRUCTION_FILE
from .models import AgentSpec, TeamSpec
from .textio import fill
from .version import __version__

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


class InstructionWriter:
    def __init__(self, command_prefix: str, answer_file: str,
                 template_dir: Path = TEMPLATE_DIR) -> None:
        self.cmd = command_prefix
        self.answer_file = answer_file
        self.template_dir = Path(template_dir)

    def _template(self, name: str) -> str:
        return (self.template_dir / name).read_text(encoding="utf-8")

    def worker_text(self, team: TeamSpec, spec: AgentSpec) -> str:
        return fill(self._template("worker.md"), name=spec.name, role=spec.role or spec.name,
                    instructions=spec.instructions, team=team.name, cmd=self.cmd,
                    answer_file=self.answer_file, version=__version__)

    def master_text(self, team: TeamSpec) -> str:
        peers = "\n".join(f"- `{a.name}` - {a.role or 'worker'}" for a in team.agents)
        return fill(self._template("master.md"), name=team.master.name,
                    role=team.master.role or "orchestrator", team=team.name, peers=peers,
                    cmd=self.cmd, version=__version__)

    def write_all(self, team: TeamSpec) -> list[Path]:
        written = [self._write(team.master.folder, self.master_text(team))]
        for spec in team.agents:
            written.append(self._write(spec.folder, self.worker_text(team, spec)))
        return written

    @staticmethod
    def _write(folder: Path, text: str) -> Path:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / INSTRUCTION_FILE
        path.write_text(text, encoding="utf-8")
        return path

    @staticmethod
    def boot_prompt(template: str, spec: AgentSpec) -> str:
        return template.replace("{name}", spec.name)
