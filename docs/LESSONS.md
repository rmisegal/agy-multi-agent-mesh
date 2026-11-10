# Lessons learned: why the first AGY mesh failed, and what agymesh does instead

Source: the session log `השוואת תקשורת בין סשנים ב-CLI.pdf` (74 pages), the PRD
`agy_mesh_prd.md` (v2.0) and the code in `L04\` (`mesh_hub.py`, `bootstrap_agent.py`,
`orchestrator.py`, `*.ps1`). Each row: what happened, the root cause, and the fix in this project.

## 1. The core problem was never solved

| # | Symptom | Root cause | agymesh fix |
|---|---|---|---|
| 1 | `inbox.ipc` appeared but the agy window did nothing (PRD failure 4) | An interactive agy REPL only reacts to typed input. AGY.md text such as "continuously watch inbox.ipc" is not a running loop. | The session runs **one blocking command**, `agymesh wait`, inside its own turn; it returns the moment a message arrives. The window is started with `agy -i "<boot prompt>"`, so it joins and enters the loop without anyone typing. |
| 2 | Pings showed "Reachable" while no agy session was involved (PRD failure 3) | The daemon answered `PONG` in Python. | The hub never answers for an agent. A PONG is a reply message posted by `agymesh reply`, run by the agy session, and it carries that session's agy pid. `ping-all` prints "answered by agy pid N". |
| 3 | Later "fixes" ran `agy -p` from the daemon, or asked the user to type "execute" in every window | Workarounds for #1: the hidden `agy -p` is a new headless process, not the open session, and typing by hand is not automation. | Not needed after #1. Mesh commands (`join`, `wait`, `reply`, `send`, `dispatch*`, `ping-all`, `mesh-check`) **refuse to run outside an agy session**: `OriginGuard` walks the process tree up to an `agy` process. |
| 4 | Orchestrator wrote the poem itself in 9 s (PRD failure 1) | No delegation rule in the system prompt. | Generated master `AGY.md` with CRITICAL DIRECTIVES; the synthesis lists missing parts instead of filling them in. |
| 5 | 20 minutes of `dir` / `Get-ChildItem` / reading 7 files (PRD failure 2) | The master had to discover how the mesh works, and polled files between LLM turns. | Master AGY.md lists the exact commands; one `dispatch`/`dispatch-all` command posts all sub-tasks first, then waits. One LLM tool call per round. |

## 2. Transport bugs in `mesh_hub.py`

| # | Bug | Consequence | Fix |
|---|---|---|---|
| 6 | `recv(4096)` taken as one whole message | TCP is a byte stream: two JSON messages glued together, or one split in two → `json.loads` fails and the connection dies silently (`except: pass`). | `LineChannel`: newline-delimited JSON, buffered until a full frame, size-capped (`max_message_bytes`). |
| 7 | Replies not correlated with requests | A leftover `response.ipc` from the previous task was read as the new answer; replies arriving out of order were attributed by sender only. | Every message has an `id`; a reply carries `reply_to`; the hub keeps a reply book keyed by id. |
| 8 | Unknown target dropped silently | `send --to art` while art's daemon was down → the sender waited until timeout with no reason. | The hub returns `unknown_peer` with the list of joined sessions, immediately. |
| 9 | Every client registered as `orchestrator_ping` / `sender_cli` / `fast_orchestrator` | Two concurrent commands overwrote each other's registry entry; replies went to the wrong socket. | Stateless request/response: one connection per request, replies fetched by id, so client names never collide. |
| 10 | One `inbox.ipc` per agent | A second message overwrote the first while the agent was busy. | One FIFO mailbox per agent in the hub, with `max_depth`, `message_ttl_s` and an overflow strategy. |
| 11 | Daemon waited forever for `response.ipc` | One stuck agent blocked its daemon permanently. | Waits are bounded on both sides (`wait_timeout_s`, `reply_timeout_s`, `ping_timeout_s`); `wait` returns `NO_MESSAGE` and the agent simply calls it again. |
| 12 | Message lost if the receiving process died mid-delivery | — | Delivery needs an `ack`; an unacknowledged message is put back at the head of the mailbox. |
| 13 | Hub lost on restart → workers silently deaf | — | `wait` re-registers the session if the hub does not know it. |

## 3. Start-up and operations

| # | Problem | Fix |
|---|---|---|
| 14 | `bootstrap_agent.py` "random jitter 1–10 s" to avoid two hubs | Jitter alone does not prevent a race, and on Windows `SO_REUSEADDR` even lets two hubs bind the same port. Agent commands (`join`/`wait`/`send`/`reply`) now auto-start a missing hub: a random delay (`hub.autostart_jitter_s`) plus a re-check spreads the agents out, and the hub binds with `SO_EXCLUSIVEADDRUSE`, so the bind itself is the single-instance lock - a loser exits and its agent connects to the winner. Measured by `tests/integration/test_autostart_race.py`: 4 agents at once, no delay → 4 spawned, 1 survived; 1.5 s delay → 1 spawned. Admin commands (`status`, `down`) never auto-start. |
| 15 | Relative paths and `python` vs. `sys.executable` made detached daemons die unseen | `HubLauncher` spawns `sys.executable -m agymesh hub` with absolute config paths and polls until the hub answers, or explains why not. |
| 15b | (found in the live test) The background hub opened an empty terminal tab | uv's `.venv\Scripts\python.exe` is a trampoline that starts the real interpreter as a child. With `DETACHED_PROCESS` the trampoline has no console, so the child allocates a new visible one. The hub is now started with `CREATE_NO_WINDOW` (a hidden console the child inherits). |
| 16 | Daemons started twice (the PC still runs 2 copies of each old daemon) | No daemons at all: the agy session is the endpoint. |
| 17 | `.ps1` blocked by ExecutionPolicy / Zone.Identifier (PRD failure 5) | No PowerShell scripts: everything is `uv run agymesh …`. |
| 18 | `accept()` blocked Ctrl+C (PRD failure 6) | Accept timeout + `agymesh down` (a `shutdown` request), no process killing by command-line match. |
| 19 | Agent list, paths, port and prompts hard-coded in 6 files; AGY.md duplicated in 3 scripts that drifted | One versioned team file + one setup file; AGY.md generated from templates. |
| 20 | Hebrew output can crash a cp1252 console; PowerShell 5 writes UTF-16 files | The CLI forces UTF-8 output; `reply --file` reads UTF-8, UTF-8-BOM and UTF-16. |

## 4. Found in the live test (2026-11-10)

| # | Observation | Cause | Fix |
|---|---|---|---|
| 21 | First real `dispatch-all` took ~4 min; the mesh itself only 23 s | 109 s inside agy before the command started, 25 s command start under memory pressure, ~30 s background-task filler turn + the master retyping the result | `--effort low`, the `.venv` launcher instead of `uv run` per call, "foreground / think briefly" rules, no retyping. Re-test: ~18 s from Enter to result. |
| 22 | Mesh-check took ~3 min | 1.00 asked the peers one at a time (~7 sequential LLM turns), plus two ~60 s stalls of the model API (`streamGenerateContent`, visible in agy's `cli-*.log`) | Peers now only POST their PINGs and reply with the message ids; the master collects every PONG from the hub's reply book by id, so all peers check in parallel without deadlock. Backend stalls remain outside our control. |
| 23 | Hebrew shown in reverse letter order in every agy window | conhost / Windows Terminal have no bidirectional text support; agy draws the chat itself | Chat is English-only (both templates); Hebrew lives only in `answer.md` and in the result, which is saved as UTF-8 `.md` + `.html` and opened in the browser. |
| 24 | In the browser, `(שקדיות וריח גשם)` showed its parentheses reversed | one `<pre dir="auto">` per answer: the browser took ONE direction from the answer's first strong letter - the Latin `text` of a Markdown fence - and laid the Hebrew line out left-to-right | one `dir="auto"` block per LINE (+ `unicode-bidi: plaintext`): each line gets its own direction; Markdown fences are dropped. Verified with a headless-Chrome screenshot of the real result. |

## 5. What remains to verify with real agy windows

The protocol is verified end-to-end by `tests/integration/test_creative_trio.py`. That test runs
a real hub, and its simulated sessions run exactly the steps in the generated AGY.md. These
agy-specific points can only be confirmed in live agy windows:

- that `agy -i "<prompt>"` keeps the session interactive after the boot prompt (per `agy --help`);
- the agy shell tool's maximum command duration. If it is shorter than `session.wait_timeout_s`
  (240 s), lower that value in `config/setup.json`;
- whether the permission mode in `launch.agy_args` lets the loop run without prompts.

---
© 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
