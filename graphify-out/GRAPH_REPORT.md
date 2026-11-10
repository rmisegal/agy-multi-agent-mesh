# Graph Report - Multi-Agent-Mesh  (2026-11-10)

## Corpus Check
- 76 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 763 nodes · 1607 edges · 53 communities (41 shown, 12 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 172 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d222b945`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Mesh Concepts & Lessons
- CLI Handlers & Errors
- Config & Team Loading
- Hub Client Gatekeeper
- Mesh Check & Orchestration
- CLI Parser & Commands
- PRD
- Mailbox Store
- Process Tree Origin
- Integration Test Fixtures
- Hub TCP Server
- test launcher instructions
- Mesh Check & Orchestration (part 4)
- Shared TODO Board
- Hub Router Ops
- hub registry and models
- Rate Gate
- Mesh Concepts & Lessons (part 5)
- Board Hub Ops
- Hub Journal
- Package Root
- CLI Handlers & Errors (part 4)
- Mesh Concepts & Lessons (part 3)
- Mesh Concepts & Lessons (part 4)
- CLI Handlers & Errors (part 2)
- INSTALL and README
- Mesh Concepts & Lessons (part 2)
- Hub TCP Server (part 2)
- CLI Handlers & Errors (part 5)
- Mesh Check & Orchestration (part 2)
- Hub Client Gatekeeper (part 2)
- USER MANUAL
- art AGY
- joke AGY
- master AGY
- poem AGY
- Mesh Check & Orchestration (part 3)
- templates master
- templates worker
- LESSONS
- PLAN
- git-hooks post checkout
- git-hooks post commit
- git-hooks post merge
- git-hooks pre commit
- setup git
- CLI Handlers & Errors (part 3)

## God Nodes (most connected - your core abstractions)
1. `Message` - 46 edges
2. `MeshError` - 44 edges
3. `AgyMesh` - 40 edges
4. `Reply` - 38 edges
5. `HubClient` - 34 edges
6. `Handlers` - 29 edges
7. `PLAN - agymesh 1.10` - 28 edges
8. `MeshConfig` - 26 edges
9. `HubRouter` - 25 edges
10. `docs/PLAN.md (document)` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Speed rules (foreground, think briefly)` --semantically_similar_to--> `Exploration overhead (PRD failure 2)`  [INFERRED] [semantically similar]
  src/agymesh/templates/worker.md → docs/PRD.md
- `TestHubClient` --uses--> `HubUnavailableError`  [INFERRED]
  tests/unit/test_client_server.py → src/agymesh/errors.py
- `TestHubServer` --uses--> `HubUnavailableError`  [INFERRED]
  tests/unit/test_client_server.py → src/agymesh/errors.py
- `TestHubLauncher` --uses--> `HubUnavailableError`  [INFERRED]
  tests/unit/test_launcher_instructions.py → src/agymesh/errors.py
- `test_send_from_plain_terminal_is_refused()` --uses--> `MeshError`  [INFERRED]
  tests/integration/test_creative_trio.py → src/agymesh/errors.py

## Import Cycles
- 4-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/hub/router_board.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/server.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`

## Hyperedges (group relationships)
- **creative-trio dispatch round (master + art, poem, joke)** — examples_creative_trio_master_agy_md, examples_creative_trio_art_agy_md, examples_creative_trio_poem_agy_md, examples_creative_trio_joke_agy_md, concept_dispatch_all, orchestrate_orchestrator [EXTRACTED 1.00]
- **Hub request pipeline: client to router to stores** — client_hubclient, protocol_linechannel, server_hubserver, router_hubrouter, mailbox_mailboxstore, registry_sessionregistry, gate_rategate, hub_journal [EXTRACTED 1.00]
- **Hebrew-safe output pattern** — concept_english_only_chat, concept_per_line_dir_auto, results_resultwriter, src_agymesh_templates_worker, src_agymesh_templates_master [INFERRED 0.85]

## Communities (53 total, 12 thin omitted)

### Community 0 - "Mesh Concepts & Lessons"
Cohesion: 0.19
Nodes (28): HubClient (API gatekeeper), Delivery ack with requeue, Hub-and-spoke localhost TCP topology, Live agy acceptance test, glb-quality-code-guidlines audit, Per-sender rate gate with client back-off, Reply correlation by message id (reply book), config/rate_limits.json (+20 more)

### Community 2 - "Config & Team Loading"
Cohesion: 0.06
Nodes (37): parametrize, check_version(), MeshConfig, Path, Read a JSON file (BOM tolerant) and raise ConfigError with the path when it…, Dotted-key access to the merged settings, with defaults as the only fallback., Resolve a path from the config relative to the project root., How an agy session invokes the CLI. Auto: the project's own ``.venv`` launcher… (+29 more)

### Community 3 - "Hub Client Gatekeeper"
Cohesion: 0.07
Nodes (17): HubClient, Stateless request/response client: one TCP connection per request., First attempt: if the hub is down and this is an agent op, start it once, retry., NotInSessionError, A mesh command was run from a plain terminal instead of from inside an agy…, OriginGuard, Stamps messages with the sending agy pid; refuses plain terminals when required., MeshContext (+9 more)

### Community 5 - "CLI Parser & Commands"
Cohesion: 0.07
Nodes (12): ArgumentParser, Namespace, Handlers, parse_tasks(), main(), Hebrew output must not crash a cp1252 Windows console., utf8_console(), _board() (+4 more)

### Community 6 - "PRD"
Cohesion: 0.09
Nodes (22): 1.1 מטרת הפרויקט, 1.2 תרחיש הייחוס (Reference Use Case), 1. תקציר מנהלים ומטרת העל (Executive Summary & Core Objective), 2. השוואת מימוש: Claude Code CLI לעומת Antigravity CLI (`agy`), 3.1 טופולוגיית הרשת ומבנה התיקיות, 3.2 זרימת הנתונים מקצה לקצה (Data Flow Lifecycle), 3. ארכיטקטורת המערכת (System Architecture), 4. ניתוח כשלים, בעיות שלמדנו בדרך והפתרונות שלהן (Post-Mortem & Lessons Learned) (+14 more)

### Community 7 - "Mailbox Store"
Cohesion: 0.10
Nodes (9): MailboxStore, Thread-safe queues with max depth, overflow strategy and message time-to-live., Put back a message whose delivery failed (e.g. the agy tool call was killed)., Message, One envelope on the mesh. ``reply_to`` links a reply to the id of its request., Clock, TestMailboxStore, send() (+1 more)

### Community 8 - "Process Tree Origin"
Cohesion: 0.07
Nodes (19): _posix_snapshot(), snapshot(), _windows_snapshot(), Proc, ProcessTable, Snapshot of the process list with ancestor walks (cycle-safe: pids can be…, AdminMixin, Path (+11 more)

### Community 9 - "Integration Test Fixtures"
Cohesion: 0.11
Nodes (18): Event, slow, mesh_factory(), Build an AgyMesh client for a given fake agy pid, connected to the live hub., fixture, test_send_from_plain_terminal_is_refused(), trio(), worker_loop() (+10 more)

### Community 10 - "Hub TCP Server"
Cohesion: 0.25
Nodes (5): exclusive_socket(), HubServer, socket, A delivered message counts only after the client confirms it; else it is…, Accept loop + one worker thread per connection.

### Community 11 - "test launcher instructions"
Cohesion: 0.06
Nodes (25): InstructionWriter, Path, detached_kwargs(), HubLauncher, Path, Starts ``python -m agymesh hub`` detached; the exclusive port bind makes it…, Return True if THIS call started the hub, False if one was already running.…, Opens one interactive agy session per agent, in the agent's own folder. (+17 more)

### Community 12 - "Mesh Check & Orchestration (part 4)"
Cohesion: 0.21
Nodes (4): AgyMesh, Path, Facade over session primitives, orchestration and administration., Mesh-check leg run by a worker: post PINGs, reply with their ids, do NOT wait.

### Community 13 - "Shared TODO Board"
Cohesion: 0.18
Nodes (4): Path, Atomically take a task (the given one, or the oldest open one). None = nothing…, TaskBoard, TestTaskBoard

### Community 14 - "Hub Router Ops"
Cohesion: 0.13
Nodes (5): HubRouter, Called by the server when a recv answer could not be written: requeue the…, Dispatches one request dict to its handler and always answers with ``{"ok":…, fixture, router()

### Community 15 - "hub registry and models"
Cohesion: 0.14
Nodes (7): Thread-safe name -> SessionInfo map; a session unseen for ``stale_after_s`` is…, SessionRegistry, DictMixin, Round-trip a dataclass through a JSON-safe dict, ignoring unknown keys., A joined agy session, the analog of Claude's ``~/.claude/sessions/<pid>.json``., SessionInfo, TestSessionRegistry

### Community 16 - "Rate Gate"
Cohesion: 0.16
Nodes (6): Exception, MeshError, Base error of the mesh; ``code`` travels over the wire in hub replies., RateGate, ``requests_per_minute`` refill rate with a ``burst_size`` bucket per sender., TestRateGate

### Community 17 - "Mesh Concepts & Lessons (part 5)"
Cohesion: 0.16
Nodes (18): TaskBoard (shared TODO board), art agent (visual artist), joke agent (Hebrew humorist), poem agent (Hebrew 4-line poet), agy -i boot prompt, Blocking wait listen loop, Passive REPL bottleneck (PRD failure 4), Speed rules (foreground, think briefly) (+10 more)

### Community 19 - "Hub Journal"
Cohesion: 0.33
Nodes (4): Journal, Path, Append-only JSON-lines log of joins and messages (for debugging and teaching)., test_journal_appends_json_lines()

### Community 26 - "CLI Handlers & Errors (part 4)"
Cohesion: 0.18
Nodes (4): Outcome of one request: the reply message, or why there is none., Reply, reply(), TestRenderer

### Community 27 - "Mesh Concepts & Lessons (part 3)"
Cohesion: 0.27
Nodes (14): CRITICAL DIRECTIVES (delegate, no exploration, one command), accept() blocks Ctrl+C (PRD failure 6), PowerShell ExecutionPolicy block (PRD failure 5), Exploration overhead (PRD failure 2), inbox.ipc / response.ipc file bridge (legacy), Master orchestrator role, Self-generation bypass (PRD failure 1), docs/PRD.md (document) (+6 more)

### Community 28 - "Mesh Concepts & Lessons (part 4)"
Cohesion: 0.25
Nodes (12): dispatch-all single-command fan-out, English-only chat language rule, Race-safe hub autostart (jitter + exclusive bind), Per-line dir=auto HTML rendering, unknown_peer explicit error, docs/LESSONS.md (document), docs/USER_MANUAL.md (document), Lessons Learned: why the first AGY mesh failed (+4 more)

### Community 29 - "CLI Handlers & Errors (part 2)"
Cohesion: 0.23
Nodes (6): _default_opener(), Path, One ``dir="auto"`` block PER LINE: each line takes its direction from its own…, ResultWriter, slug(), TestResultWriter

### Community 30 - "INSTALL and README"
Cohesion: 0.14
Nodes (13): 0. The fastest way — one script does everything, 1. What you need, 2. Install, 3. First start, 4. Settings you may need to change, 5. Update / uninstall, 6. Installation problems, Installation guide — agymesh 1.11 (+5 more)

### Community 31 - "Mesh Concepts & Lessons (part 2)"
Cohesion: 0.29
Nodes (12): Antigravity CLI (agy), Claude Code ListAgents/SendMessage analogy, Fake PONG daemon shortcut (PRD failure 3), Messages stamped with sender agy pid, Project knowledge graph stored gzipped in git, uv package manager, config/setup.json, README.md (document) (+4 more)

### Community 32 - "Hub TCP Server (part 2)"
Cohesion: 0.24
Nodes (7): ProtocolError, A frame on the wire is not valid JSON or is too large., LineChannel, socket, One JSON object per line, UTF-8, never more than ``max_bytes`` per frame., Return the next frame, or None when the peer closed the connection., TestLineChannel

### Community 34 - "Mesh Check & Orchestration (part 2)"
Cohesion: 0.33
Nodes (5): MeshChecker, parse_sent(), ``{"sent": {peer: ping_id}}`` from a peer's meshcheck reply; {} if malformed., FakeOrch, TestMeshChecker

### Community 35 - "Hub Client Gatekeeper (part 2)"
Cohesion: 0.27
Nodes (3): Orchestrator, Sender side of the mesh, used by the master and by workers running ``ping-all``., Wait for the replies to any request ids (``key -> id``) under one shared…

### Community 37 - "USER MANUAL"
Cohesion: 0.25
Nodes (8): 1. The idea in five sentences, 2. The example team: master + art, poem, joke, 3. How many sub-agents? — the team file, 4. A shared TODO list — the board (and how it differs from the inbox), 5. Everyday operation, 6. Command reference, 7. Troubleshooting, User manual — agymesh 1.11

### Community 38 - "art AGY"
Cohesion: 0.25
Nodes (7): AGY Mesh Agent: `art`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub), Speed rules

### Community 39 - "joke AGY"
Cohesion: 0.25
Nodes (7): AGY Mesh Agent: `joke`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub), Speed rules

### Community 40 - "master AGY"
Cohesion: 0.25
Nodes (7): AGY Mesh Master: `master`, Commands (run them with your shell tool), CRITICAL DIRECTIVES, Language rule, Shared TODO board (for goals with many small tasks), Speed rules, Workflow for any user goal

### Community 41 - "poem AGY"
Cohesion: 0.25
Nodes (7): AGY Mesh Agent: `poem`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub), Speed rules

### Community 43 - "templates master"
Cohesion: 0.29
Nodes (7): AGY Mesh Master: `{{name}}`, Commands (run them with your shell tool), CRITICAL DIRECTIVES, Language rule, Shared TODO board (for goals with many small tasks), Speed rules, Workflow for any user goal

### Community 44 - "templates worker"
Cohesion: 0.29
Nodes (7): AGY Mesh Agent: `{{name}}`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub), Speed rules

### Community 45 - "LESSONS"
Cohesion: 0.33
Nodes (6): 1. The core problem was never solved, 2. Transport bugs in `mesh_hub.py`, 3. Start-up and operations, 4. Found in the live test (2026-11-10), 5. What remains to verify with real agy windows, Lessons learned: why the first AGY mesh failed, and what agymesh does instead

### Community 46 - "PLAN"
Cohesion: 0.40
Nodes (5): 1. Architecture, 2. PRD coverage (`agy_mesh_prd.md` v2.0), 3. Quality audit (`/glb-quality-code-guidlines`), 4. Acceptance with live agy windows (manual), PLAN — agymesh 1.11

## Knowledge Gaps
- **86 isolated node(s):** `agymesh`, `examples/creative-trio/art/AGY.md (document)`, `examples/creative-trio/joke/AGY.md (document)`, `examples/creative-trio/poem/AGY.md (document)`, `src/agymesh/templates/master.md (document)` (+81 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgyMesh` connect `Mesh Check & Orchestration (part 4)` to `CLI Handlers & Errors (part 5)`, `CLI Handlers & Errors`, `Mesh Check & Orchestration (part 2)`, `Mesh Check & Orchestration`, `CLI Parser & Commands`, `Hub Client Gatekeeper (part 2)`, `Mailbox Store`, `Process Tree Origin`, `Hub Client Gatekeeper`, `Mesh Check & Orchestration (part 3)`, `Config & Team Loading`, `Integration Test Fixtures`, `Rate Gate`, `CLI Handlers & Errors (part 4)`, `CLI Handlers & Errors (part 2)`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `MeshError` connect `Rate Gate` to `Hub TCP Server (part 2)`, `CLI Handlers & Errors (part 5)`, `Config & Team Loading`, `Hub Client Gatekeeper`, `CLI Handlers & Errors`, `CLI Parser & Commands`, `Hub Client Gatekeeper (part 2)`, `Mailbox Store`, `Integration Test Fixtures`, `test launcher instructions`, `Mesh Check & Orchestration (part 4)`, `Shared TODO Board`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Message` connect `Mailbox Store` to `CLI Handlers & Errors`, `CLI Handlers & Errors (part 5)`, `Hub Client Gatekeeper (part 2)`, `Mesh Check & Orchestration`, `Hub Client Gatekeeper`, `Mesh Check & Orchestration (part 2)`, `test launcher instructions`, `Mesh Check & Orchestration (part 4)`, `hub registry and models`, `CLI Handlers & Errors (part 4)`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Message` (e.g. with `Orchestrator` and `Reply`) actually correct?**
  _`Message` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MeshError` (e.g. with `HubClient` and `TerminalLauncher`) actually correct?**
  _`MeshError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `AgyMesh` (e.g. with `MeshError` and `MeshChecker`) actually correct?**
  _`AgyMesh` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Reply` (e.g. with `Message` and `Renderer`) actually correct?**
  _`Reply` has 8 INFERRED edges - model-reasoned connections that need verification._