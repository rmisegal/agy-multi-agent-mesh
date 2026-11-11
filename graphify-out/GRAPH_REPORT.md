# Graph Report - mesh-pr  (2026-11-11)

## Corpus Check
- 75 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 803 nodes · 1789 edges · 46 communities (31 shown, 15 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 192 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0620d605`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_PLAN|PLAN]]
- [[_COMMUNITY_hub server (part 3)|hub server (part 3)]]
- [[_COMMUNITY_Config & Team Loading|Config & Team Loading]]
- [[_COMMUNITY_Hub Router Ops (part 2)|Hub Router Ops (part 2)]]
- [[_COMMUNITY_Mesh Check & Orchestration|Mesh Check & Orchestration]]
- [[_COMMUNITY_CLI Parser & Commands|CLI Parser & Commands]]
- [[_COMMUNITY_PRD|PRD]]
- [[_COMMUNITY_Mailbox Store|Mailbox Store]]
- [[_COMMUNITY_Process Tree Origin|Process Tree Origin]]
- [[_COMMUNITY_Integration Test Fixtures|Integration Test Fixtures]]
- [[_COMMUNITY_hub server|hub server]]
- [[_COMMUNITY_test launcher instructions (part 2)|test launcher instructions (part 2)]]
- [[_COMMUNITY_Mesh Check & Orchestration (part 4)|Mesh Check & Orchestration (part 4)]]
- [[_COMMUNITY_Shared TODO Board|Shared TODO Board]]
- [[_COMMUNITY_Hub Router Ops|Hub Router Ops]]
- [[_COMMUNITY_hub registry and models|hub registry and models]]
- [[_COMMUNITY_Process Tree Origin (part 2)|Process Tree Origin (part 2)]]
- [[_COMMUNITY_art AGY|art AGY]]
- [[_COMMUNITY__src build|_src build]]
- [[_COMMUNITY_test client server|test client server]]
- [[_COMMUNITY_Package Root|Package Root]]
- [[_COMMUNITY_CLI Package|CLI Package]]
- [[_COMMUNITY_Hub Package|Hub Package]]
- [[_COMMUNITY_Tests Package|Tests Package]]
- [[_COMMUNITY_Integration Package|Integration Package]]
- [[_COMMUNITY_Unit Package|Unit Package]]
- [[_COMMUNITY_CLI Handlers & Errors (part 4)|CLI Handlers & Errors (part 4)]]
- [[_COMMUNITY__src OUTLINE|_src OUTLINE]]
- [[_COMMUNITY_art AGY (2)|art AGY (2)]]
- [[_COMMUNITY_CLI Handlers & Errors (part 2)|CLI Handlers & Errors (part 2)]]
- [[_COMMUNITY_PLAN (part 2)|PLAN (part 2)]]
- [[_COMMUNITY_test jobs and jobs|test jobs and jobs]]
- [[_COMMUNITY_test launcher instructions|test launcher instructions]]
- [[_COMMUNITY_hub server (part 6)|hub server (part 6)]]
- [[_COMMUNITY_Mesh Check & Orchestration (part 2)|Mesh Check & Orchestration (part 2)]]
- [[_COMMUNITY_Hub Client Gatekeeper (part 2)|Hub Client Gatekeeper (part 2)]]
- [[_COMMUNITY_hub server (part 5)|hub server (part 5)]]
- [[_COMMUNITY_hub server (part 2)|hub server (part 2)]]
- [[_COMMUNITY_Mesh Check & Orchestration (part 3)|Mesh Check & Orchestration (part 3)]]
- [[_COMMUNITY_git-hooks post checkout|git-hooks post checkout]]
- [[_COMMUNITY_git-hooks post commit|git-hooks post commit]]
- [[_COMMUNITY_git-hooks post merge|git-hooks post merge]]
- [[_COMMUNITY_git-hooks pre commit|git-hooks pre commit]]
- [[_COMMUNITY_setup git|setup git]]

## God Nodes (most connected - your core abstractions)
1. `Message` - 46 edges
2. `MeshError` - 44 edges
3. `AgyMesh` - 40 edges
4. `Reply` - 38 edges
5. `HubClient` - 34 edges
6. `docs/PRD.md (document)` - 34 edges
7. `docs/PLAN.md (document)` - 30 edges
8. `Handlers` - 29 edges
9. `PLAN - agymesh 1.10` - 28 edges
10. `MeshConfig` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_journal_appends_json_lines()` --uses--> `Journal`  [INFERRED]
  tests/unit/test_router_protocol.py → src/agymesh/hub/server.py
- `Speed rules (foreground, think briefly)` --semantically_similar_to--> `Exploration overhead (PRD failure 2)`  [INFERRED] [semantically similar]
  src/agymesh/templates/worker.md → docs/PRD.md
- `test_send_from_plain_terminal_is_refused()` --uses--> `MeshError`  [INFERRED]
  tests/integration/test_creative_trio.py → src/agymesh/errors.py
- `TestTaskBoard` --uses--> `MeshError`  [INFERRED]
  tests/unit/test_board.py → src/agymesh/errors.py
- `test_parse_tasks()` --uses--> `MeshError`  [INFERRED]
  tests/unit/test_cli.py → src/agymesh/errors.py

## Import Cycles
- 4-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/hub/router_board.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/server.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`

## Hyperedges (group relationships)
- **creative-trio dispatch round (master + art, poem, joke)** — examples_creative_trio_master_agy_md, examples_creative_trio_art_agy_md, examples_creative_trio_poem_agy_md, examples_creative_trio_joke_agy_md, concept_dispatch_all, orchestrate_orchestrator [EXTRACTED 1.00]
- **Hub request pipeline: client to router to stores** — client_hubclient, protocol_linechannel, server_hubserver, router_hubrouter, mailbox_mailboxstore, registry_sessionregistry, gate_rategate, hub_journal [EXTRACTED 1.00]
- **Hebrew-safe output pattern** — concept_english_only_chat, concept_per_line_dir_auto, results_resultwriter, src_agymesh_templates_worker, src_agymesh_templates_master [INFERRED 0.85]

## Communities (46 total, 15 thin omitted)

### Community 0 - "PLAN"
Cohesion: 0.06
Nodes (82): TaskBoard (shared TODO board), HubClient (API gatekeeper), Delivery ack with requeue, art agent (visual artist), joke agent (Hebrew humorist), poem agent (Hebrew 4-line poet), Claude Code ListAgents/SendMessage analogy, accept() blocks Ctrl+C (PRD failure 6) (+74 more)

### Community 1 - "hub server (part 3)"
Cohesion: 0.22
Nodes (6): Exception, HubUnavailableError, MeshError, Base error of the mesh; ``code`` travels over the wire in hub replies., The hub is not running or cannot be reached., TestRateGate

### Community 2 - "Config & Team Loading"
Cohesion: 0.06
Nodes (36): parametrize, check_version(), MeshConfig, Path, Read a JSON file (BOM tolerant) and raise ConfigError with the path when it…, Dotted-key access to the merged settings, with defaults as the only fallback., Resolve a path from the config relative to the project root., How an agy session invokes the CLI. Auto: the project's own ``.venv`` launcher… (+28 more)

### Community 3 - "Hub Router Ops (part 2)"
Cohesion: 0.22
Nodes (3): RateGate, ``requests_per_minute`` refill rate with a ``burst_size`` bucket per sender., Clock

### Community 5 - "CLI Parser & Commands"
Cohesion: 0.06
Nodes (12): ArgumentParser, Namespace, Handlers, parse_tasks(), main(), Hebrew output must not crash a cp1252 Windows console., utf8_console(), _board() (+4 more)

### Community 6 - "PRD"
Cohesion: 0.07
Nodes (54): agy -i boot prompt, CRITICAL DIRECTIVES (delegate, no exploration, one command), dispatch-all single-command fan-out, PowerShell ExecutionPolicy block (PRD failure 5), Exploration overhead (PRD failure 2), inbox.ipc / response.ipc file bridge (legacy), Master orchestrator role, Passive REPL bottleneck (PRD failure 4) (+46 more)

### Community 7 - "Mailbox Store"
Cohesion: 0.09
Nodes (11): MailboxStore, Thread-safe queues with max depth, overflow strategy and message time-to-live., Put back a message whose delivery failed (e.g. the agy tool call was killed)., DictMixin, Message, Round-trip a dataclass through a JSON-safe dict, ignoring unknown keys., One envelope on the mesh. ``reply_to`` links a reply to the id of its request., TestModels (+3 more)

### Community 8 - "Process Tree Origin"
Cohesion: 0.10
Nodes (16): NotInSessionError, A mesh command was run from a plain terminal instead of from inside an agy…, _posix_snapshot(), snapshot(), _windows_snapshot(), OriginGuard, Proc, ProcessTable (+8 more)

### Community 9 - "Integration Test Fixtures"
Cohesion: 0.11
Nodes (19): Event, slow, mesh_factory(), Build an AgyMesh client for a given fake agy pid, connected to the live hub., fixture, test_send_from_plain_terminal_is_refused(), trio(), worker_loop() (+11 more)

### Community 10 - "hub server"
Cohesion: 0.13
Nodes (12): ProtocolError, A frame on the wire is not valid JSON or is too large., exclusive_socket(), HubServer, socket, A delivered message counts only after the client confirms it; else it is…, Accept loop + one worker thread per connection., LineChannel (+4 more)

### Community 11 - "test launcher instructions (part 2)"
Cohesion: 0.08
Nodes (23): AgentSpec, Open the window OUTSIDE the caller's job object when that is allowed.          a, Starts ``python -m agymesh hub`` detached; the exclusive port bind makes it sing, Return True if THIS call started the hub, False if one was already running., float, HubClient, Path, detached_kwargs() (+15 more)

### Community 12 - "Mesh Check & Orchestration (part 4)"
Cohesion: 0.21
Nodes (4): AgyMesh, Path, Facade over session primitives, orchestration and administration., Mesh-check leg run by a worker: post PINGs, reply with their ids, do NOT wait.

### Community 13 - "Shared TODO Board"
Cohesion: 0.11
Nodes (6): Path, Atomically take a task (the given one, or the oldest open one). None = nothing…, TaskBoard, BoardOpsMixin, Needs ``self.board`` (TaskBoard) and ``self.journal``; registers its ops in…, TestTaskBoard

### Community 14 - "Hub Router Ops"
Cohesion: 0.14
Nodes (3): HubRouter, Called by the server when a recv answer could not be written: requeue the…, Dispatches one request dict to its handler and always answers with ``{"ok":…

### Community 15 - "hub registry and models"
Cohesion: 0.19
Nodes (5): Thread-safe name -> SessionInfo map; a session unseen for ``stale_after_s`` is…, SessionRegistry, A joined agy session, the analog of Claude's ``~/.claude/sessions/<pid>.json``., SessionInfo, TestSessionRegistry

### Community 16 - "Process Tree Origin (part 2)"
Cohesion: 0.14
Nodes (8): AdminMixin, Path, Operations that set the mesh up; they may run from any terminal., Operations that set the mesh up; they may run from any terminal., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port., Open agy windows. ``ping_test``: the master runs the PING/PONG check after…, Block until ``count`` workers (default: the whole team) have joined; returns…

### Community 17 - "art AGY"
Cohesion: 0.42
Nodes (9): examples/creative-trio/joke/AGY.md (document), joke/AGY.md, AGY Mesh Agent: `joke`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub) (+1 more)

### Community 18 - "_src build"
Cohesion: 0.60
Nodes (5): add_watermarks(), assemble(), inline_images(), main(), validate()

### Community 19 - "test client server"
Cohesion: 0.06
Nodes (17): HubClient, Stateless request/response client: one TCP connection per request., First attempt: if the hub is down and this is an agent op, start it once, retry., InstructionWriter, Path, Path, A whole team: one master plus any number of worker agents., TeamSpec (+9 more)

### Community 26 - "CLI Handlers & Errors (part 4)"
Cohesion: 0.22
Nodes (4): Outcome of one request: the reply message, or why there is none., Reply, reply(), TestRenderer

### Community 28 - "art AGY (2)"
Cohesion: 0.13
Nodes (26): examples/creative-trio/art/AGY.md (document), examples/creative-trio/poem/AGY.md (document), src/agymesh/templates/worker.md (document), art/AGY.md, AGY Mesh Agent: `art`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh") (+18 more)

### Community 29 - "CLI Handlers & Errors (part 2)"
Cohesion: 0.23
Nodes (6): _default_opener(), Path, One ``dir="auto"`` block PER LINE: each line takes its direction from its own…, ResultWriter, slug(), TestResultWriter

### Community 30 - "PLAN (part 2)"
Cohesion: 0.24
Nodes (14): Antigravity CLI (agy), uv package manager, config/setup.json, docs/INSTALL.md (document), 0. The fastest way — one script does everything, 1. What you need, 2. Install, 3. First start (+6 more)

### Community 31 - "test jobs and jobs"
Cohesion: 0.24
Nodes (10): job_kills_children(), _query_kill_on_close(), True when the current process is in a job that kills its processes when it close, bool, int, str, probe(), test_detects_agy_style_job_that_kills_on_close() (+2 more)

### Community 32 - "test launcher instructions"
Cohesion: 0.33
Nodes (6): fill(), Path, Read an answer file whatever wrote it: UTF-8, UTF-8 with BOM, or UTF-16…, Replace ``{{key}}`` placeholders; unknown placeholders are left untouched., read_text_any(), test_textio_reads_any_encoding_and_fills()

### Community 33 - "hub server (part 6)"
Cohesion: 0.25
Nodes (3): Journal, Path, Append-only JSON-lines log of joins and messages (for debugging and teaching).

### Community 34 - "Mesh Check & Orchestration (part 2)"
Cohesion: 0.21
Nodes (6): MeshChecker, MeshReport, parse_sent(), ``{"sent": {peer: ping_id}}`` from a peer's meshcheck reply; {} if malformed., FakeOrch, TestMeshChecker

### Community 35 - "Hub Client Gatekeeper (part 2)"
Cohesion: 0.31
Nodes (3): Orchestrator, Sender side of the mesh, used by the master and by workers running ``ping-all``., Wait for the replies to any request ids (``key -> id``) under one shared…

### Community 37 - "hub server (part 5)"
Cohesion: 0.36
Nodes (4): agymesh/__init__.py, fixture, router(), test_journal_appends_json_lines()

## Knowledge Gaps
- **14 isolated node(s):** `agymesh`, `cli/__init__.py`, `hub/__init__.py`, `tests/__init__.py`, `integration/__init__.py` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MeshError` connect `hub server (part 3)` to `Config & Team Loading`, `Hub Router Ops (part 2)`, `Hub Client Gatekeeper (part 2)`, `CLI Parser & Commands`, `hub server (part 5)`, `Mailbox Store`, `Process Tree Origin`, `hub server (part 4)`, `hub server`, `test launcher instructions (part 2)`, `Mesh Check & Orchestration (part 4)`, `Shared TODO Board`, `Hub Router Ops`, `Integration Test Fixtures`, `test client server`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `AgyMesh` connect `Mesh Check & Orchestration (part 4)` to `hub server (part 3)`, `Mesh Check & Orchestration (part 2)`, `Hub Client Gatekeeper (part 2)`, `Config & Team Loading`, `hub server (part 5)`, `CLI Parser & Commands`, `Mailbox Store`, `Integration Test Fixtures`, `Mesh Check & Orchestration (part 3)`, `Process Tree Origin (part 2)`, `test client server`, `CLI Handlers & Errors (part 4)`, `CLI Handlers & Errors (part 2)`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Message` connect `Mailbox Store` to `hub server (part 3)`, `Mesh Check & Orchestration (part 2)`, `Hub Client Gatekeeper (part 2)`, `Mesh Check & Orchestration`, `hub server (part 5)`, `hub server (part 4)`, `Mesh Check & Orchestration (part 4)`, `test client server`, `CLI Handlers & Errors (part 4)`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Message` (e.g. with `Orchestrator` and `Reply`) actually correct?**
  _`Message` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MeshError` (e.g. with `HubClient` and `TerminalLauncher`) actually correct?**
  _`MeshError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `AgyMesh` (e.g. with `MeshError` and `MeshChecker`) actually correct?**
  _`AgyMesh` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Reply` (e.g. with `Message` and `Renderer`) actually correct?**
  _`Reply` has 8 INFERRED edges - model-reasoned connections that need verification._