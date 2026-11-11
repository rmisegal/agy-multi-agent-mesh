# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubLauncher (start the hub once, in the background) and TerminalLauncher (open agy windows).

No PowerShell scripts are involved, so ExecutionPolicy / Zone.Identifier blocks cannot occur.
Each agy window starts with ``agy -i "<boot prompt>"``: the session reads its AGY.md and enters
the listen loop by itself - the user never has to type "start listening" into every window.
"""

from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

from .client import HubClient
from .constants import ENV_CONFIG_DIR
from .errors import HubUnavailableError, MeshError
from .jobs import CONTAINED_HINT, job_kills_children
from .models import AgentSpec

BREAKAWAY = 0x01000000  # CREATE_BREAKAWAY_FROM_JOB: survive the agy tool-call job object


def detached_kwargs(breakaway: bool) -> dict:
    if sys.platform != "win32":  # pragma: no cover - POSIX
        return {"start_new_session": True}
    # CREATE_NO_WINDOW, not DETACHED_PROCESS: uv's .venv python.exe is a trampoline that starts
    # the real interpreter as a child. A detached trampoline has no console, so the child would
    # allocate a NEW visible one (an empty terminal tab). A hidden console is inherited instead.
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    return {"creationflags": flags | (BREAKAWAY if breakaway else 0)}


class HubLauncher:
    """Starts ``python -m agymesh hub`` detached; the exclusive port bind makes it single-instance."""

    def __init__(self, client: HubClient, config_dir: Path, start_wait_s: float = 8.0,
                 poll_s: float = 0.2, spawn: Callable = subprocess.Popen,
                 sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic,
                 jitter_s: float = 0.0,
                 rand: Callable[[float, float], float] = random.uniform,
                 job_kills: Callable[[], bool] = job_kills_children) -> None:
        self.client = client
        self.config_dir = Path(config_dir)
        self.start_wait_s, self.poll_s = start_wait_s, poll_s
        self.spawn, self.sleep, self.clock = spawn, sleep, clock
        self.jitter_s, self.rand, self.job_kills = jitter_s, rand, job_kills

    def command(self) -> list[str]:
        return [sys.executable, "-m", "agymesh", "hub"]

    def ensure(self) -> bool:
        """Return True if THIS call started the hub, False if one was already running.

        Race-safe when many agents call it at once: (1) a random delay spreads them out and
        each re-checks after it, so usually only the first one spawns; (2) if two still spawn,
        the hub binds its port EXCLUSIVELY - the loser cannot bind and exits, and every caller
        then connects to the single winner. The delay only saves work; the bind is the lock.
        """
        if self.client.is_up():
            return False
        if self.jitter_s > 0:
            self.sleep(self.rand(0.0, self.jitter_s))
            if self.client.is_up():
                return False
        env = {**os.environ, ENV_CONFIG_DIR: str(self.config_dir)}
        io = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
              "stderr": subprocess.DEVNULL, "close_fds": True, "env": env}
        try:
            self.spawn(self.command(), **io, **detached_kwargs(breakaway=True))
        except OSError:
            if self.job_kills():  # a hub started here would die with this command
                raise HubUnavailableError(CONTAINED_HINT.format(what="hub")) from None
            self.spawn(self.command(), **io, **detached_kwargs(breakaway=False))
        deadline = self.clock() + self.start_wait_s
        while self.clock() < deadline:
            if self.client.is_up():
                return True
            self.sleep(self.poll_s)
        raise HubUnavailableError(
            f"the hub did not start within {self.start_wait_s}s; run `agymesh hub` in a "
            "terminal to see the reason"
        )


class TerminalLauncher:
    """Opens one interactive agy session per agent, in the agent's own folder."""

    def __init__(self, agy_exe: str, agy_args: list[str], terminal: str = "console",
                 spawn: Callable = subprocess.Popen,
                 which: Callable[[str], str | None] = shutil.which,
                 job_kills: Callable[[], bool] = job_kills_children) -> None:
        self.agy_exe, self.agy_args, self.terminal = agy_exe, list(agy_args), terminal
        self.spawn, self.which, self.job_kills = spawn, which, job_kills

    def open(self, spec: AgentSpec, boot_prompt: str) -> list[str]:
        exe = self.which(self.agy_exe)
        if not exe:
            raise MeshError(f"'{self.agy_exe}' was not found on PATH; install Antigravity CLI")
        spec.folder.mkdir(parents=True, exist_ok=True)
        argv = [exe, *self.agy_args, "-i", boot_prompt]
        wt = self.which("wt") if self.terminal == "wt" else None
        if wt:
            safe = [a.replace(";", ",") for a in argv]  # ';' separates wt commands
            self._spawn_windows([wt, "-w", "0", "nt", "-d", str(spec.folder),
                                 "--title", f"agy:{spec.name}", *safe], 0)
        elif sys.platform == "win32":
            self._spawn_windows(argv, subprocess.CREATE_NEW_CONSOLE, cwd=str(spec.folder))
        else:  # pragma: no cover - POSIX: runs in the current terminal's session
            self.spawn(argv, cwd=str(spec.folder), start_new_session=True)
        return argv

    def _spawn_windows(self, argv: list[str], flags: int, **kw) -> None:
        """Open the window OUTSIDE the caller's job object when that is allowed.

        agy runs every shell command inside a job that is closed when the tool call returns,
        and a job takes its child processes with it - so `agymesh up` run BY an agy session
        used to open the windows and lose them a moment later. If the job forbids breakaway:
        refuse with a clear message when it would kill the window (agy's case), otherwise open
        the window without breakaway (it then lives as long as the caller).
        """
        if sys.platform != "win32":  # pragma: no cover - wt is Windows-only
            self.spawn(argv, **kw)
            return
        try:
            self.spawn(argv, creationflags=flags | BREAKAWAY, **kw)
        except OSError:
            if self.job_kills():
                raise MeshError(CONTAINED_HINT.format(what="agy windows")) from None
            self.spawn(argv, creationflags=flags, **kw)
