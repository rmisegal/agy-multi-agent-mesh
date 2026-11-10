# Installation guide — agymesh 1.10

© 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.

## 1. What you need

| Tool | Why | How to check |
|---|---|---|
| Windows 10/11 (PowerShell 7 recommended) | agy windows are opened as Windows consoles | `$PSVersionTable.PSVersion` |
| **Antigravity CLI (`agy`)**, logged in | the agents themselves | `agy --help`; run `agy` once and sign in |
| **uv** (Python package manager) | installs Python + agymesh | `uv --version` |
| **Git** | download the project | `git --version` |

Install `uv` if it is missing (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`uv` downloads a suitable Python (≥ 3.10) by itself; you do not need to install Python first.
agymesh has **no third-party runtime dependencies**.

## 2. Install

```powershell
cd C:\Users\<you>\projects            # any folder WITHOUT Hebrew characters in the path
git clone https://github.com/rmisegal/agy-multi-agent-mesh.git
cd agy-multi-agent-mesh
uv sync                                # creates .venv and installs agymesh into it
uv run agymesh --version               # -> agymesh 1.10 - © 2026 Dr. Yoram Segal ...
```

Optional — run the test suite (about 30 s; 90 tests):

```powershell
uv run pytest -q
```

## 3. First start

```powershell
uv run agymesh up --with-master
```

This starts the hub, writes `AGY.md` into every agent folder **for your machine** (the generated
commands contain your install path), and opens one agy window per agent plus the master.

The first time, every agy window asks **"Do you trust the contents of this project?"** — choose
*Yes, I trust this folder* in each window. agy remembers it; you are not asked again.

Check that everyone joined (in your normal PowerShell window):

```powershell
uv run agymesh status       # art, poem, joke: state "listening", each with an agy pid
```

Continue with the [User manual](USER_MANUAL.md).

## 4. Settings you may need to change

All settings are in `config/setup.json` (version `1.00`). The most common ones:

| Setting | Default | Change it when |
|---|---|---|
| `hub.port` | `9877` | another program uses the port (or set env `AGYMESH_PORT`) |
| `launch.agy_args` | `--dangerously-skip-permissions --effort low` | you want agy to ask before every command (remove the first flag) |
| `launch.terminal` | `console` | you prefer tabs in Windows Terminal: `wt` |
| `session.wait_timeout_s` | `240` | agy cuts long commands off earlier than that |
| `orchestrator.open_result` | `true` | you do not want the browser to open results |
| `team_file` | `examples/creative-trio/team.json` | you use your own team (or `--team <file>`) |

## 5. Update / uninstall

```powershell
git pull; uv sync            # update
uv run agymesh down          # stop the hub, then delete the folder to uninstall
```

## 6. Installation problems

| Symptom | Fix |
|---|---|
| `uv` is not recognized | open a NEW terminal after installing uv |
| `'agy' was not found on PATH` | install Antigravity CLI and open a new terminal |
| `port 127.0.0.1:9877 is already taken` | set `AGYMESH_PORT=9878` (or edit `hub.port`) |
| `ERROR: This mesh command must be run BY an agy session` | correct behavior: agent commands are run by the agy windows, not by you. For a one-off test add `--allow-external`. |
| A window shows a trust or permission question | answer it once in that window |
