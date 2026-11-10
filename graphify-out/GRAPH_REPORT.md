# Graph Report - Multi-Agent-Mesh  (2026-11-10)

## Corpus Check
- 78 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 772 nodes · 1722 edges · 42 communities (32 shown, 10 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 172 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `568d395f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PLAN
- agymesh errors
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
- Process Tree Origin (part 2)
- art AGY
- _src build
- Hub Journal
- Package Root
- CLI Handlers & Errors (part 4)
- _src OUTLINE
- CLI Handlers & Errors (part 2)
- Hub TCP Server (part 2)
- agymesh models
- Mesh Check & Orchestration (part 2)
- Hub Client Gatekeeper (part 2)
- master AGY and USER MANUAL
- poem AGY
- Mesh Check & Orchestration (part 3)
- git-hooks post checkout
- git-hooks post commit
- git-hooks post merge
- git-hooks pre commit
- setup git

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
- `TestHubClient` --uses--> `HubUnavailableError`  [INFERRED]
  tests/unit/test_client_server.py → src/agymesh/errors.py
- `TestHubLauncher` --uses--> `HubUnavailableError`  [INFERRED]
  tests/unit/test_launcher_instructions.py → src/agymesh/errors.py
- `race_env()` --uses--> `HubLauncher`  [INFERRED]
  tests/integration/test_autostart_race.py → src/agymesh/launcher.py

## Import Cycles
- 4-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/hub/router_board.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/server.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`

## Hyperedges (group relationships)
- **creative-trio dispatch round (master + art, poem, joke)** — examples_creative_trio_master_agy_md, examples_creative_trio_art_agy_md, examples_creative_trio_poem_agy_md, examples_creative_trio_joke_agy_md, concept_dispatch_all, orchestrate_orchestrator [EXTRACTED 1.00]
- **Hub request pipeline: client to router to stores** — client_hubclient, protocol_linechannel, server_hubserver, router_hubrouter, mailbox_mailboxstore, registry_sessionregistry, gate_rategate, hub_journal [EXTRACTED 1.00]
- **Hebrew-safe output pattern** — concept_english_only_chat, concept_per_line_dir_auto, results_resultwriter, src_agymesh_templates_worker, src_agymesh_templates_master [INFERRED 0.85]

## Communities (42 total, 10 thin omitted)

### Community 0 - "PLAN"
Cohesion: 0.06
Nodes (73): HubClient (API gatekeeper), Delivery ack with requeue, Antigravity CLI (agy), English-only chat language rule, Fake PONG daemon shortcut (PRD failure 3), Hub-and-spoke localhost TCP topology, Race-safe hub autostart (jitter + exclusive bind), Live agy acceptance test (+65 more)

### Community 1 - "agymesh errors"
Cohesion: 0.21
Nodes (4): Exception, MeshError, Base error of the mesh; ``code`` travels over the wire in hub replies., test_journal_appends_json_lines()

### Community 2 - "Config & Team Loading"
Cohesion: 0.07
Nodes (34): parametrize, check_version(), MeshConfig, Path, Read a JSON file (BOM tolerant) and raise ConfigError with the path when it…, Dotted-key access to the merged settings, with defaults as the only fallback., Resolve a path from the config relative to the project root., How an agy session invokes the CLI. Auto: the project's own ``.venv`` launcher… (+26 more)

### Community 3 - "Hub Client Gatekeeper"
Cohesion: 0.09
Nodes (11): HubClient, Stateless request/response client: one TCP connection per request., First attempt: if the hub is down and this is an agent op, start it once, retry., MeshContext, Path, Lazy factory. ``allow_external`` disables the in-session check for diagnostics…, Path, In-session commands. Every call is stamped with the agy pid by the OriginGuard. (+3 more)

### Community 5 - "CLI Parser & Commands"
Cohesion: 0.06
Nodes (12): ArgumentParser, Namespace, Handlers, parse_tasks(), main(), Hebrew output must not crash a cp1252 Windows console., utf8_console(), _board() (+4 more)

### Community 6 - "PRD"
Cohesion: 0.11
Nodes (34): agy -i boot prompt, Claude Code ListAgents/SendMessage analogy, accept() blocks Ctrl+C (PRD failure 6), PowerShell ExecutionPolicy block (PRD failure 5), inbox.ipc / response.ipc file bridge (legacy), Master orchestrator role, Passive REPL bottleneck (PRD failure 4), Self-generation bypass (PRD failure 1) (+26 more)

### Community 7 - "Mailbox Store"
Cohesion: 0.10
Nodes (10): MailboxStore, Thread-safe queues with max depth, overflow strategy and message time-to-live., Put back a message whose delivery failed (e.g. the agy tool call was killed)., DictMixin, Message, Round-trip a dataclass through a JSON-safe dict, ignoring unknown keys., One envelope on the mesh. ``reply_to`` links a reply to the id of its request., TestMailboxStore (+2 more)

### Community 8 - "Process Tree Origin"
Cohesion: 0.10
Nodes (16): NotInSessionError, A mesh command was run from a plain terminal instead of from inside an agy…, _posix_snapshot(), snapshot(), _windows_snapshot(), OriginGuard, Proc, ProcessTable (+8 more)

### Community 9 - "Integration Test Fixtures"
Cohesion: 0.11
Nodes (18): Event, slow, mesh_factory(), Build an AgyMesh client for a given fake agy pid, connected to the live hub., fixture, test_send_from_plain_terminal_is_refused(), trio(), worker_loop() (+10 more)

### Community 10 - "Hub TCP Server"
Cohesion: 0.16
Nodes (8): HubUnavailableError, The hub is not running or cannot be reached., exclusive_socket(), HubServer, socket, A delivered message counts only after the client confirms it; else it is…, Accept loop + one worker thread per connection., TestHubServer

### Community 11 - "test launcher instructions"
Cohesion: 0.06
Nodes (28): InstructionWriter, Path, detached_kwargs(), HubLauncher, Path, Starts ``python -m agymesh hub`` detached; the exclusive port bind makes it…, Return True if THIS call started the hub, False if one was already running.…, Opens one interactive agy session per agent, in the agent's own folder. (+20 more)

### Community 12 - "Mesh Check & Orchestration (part 4)"
Cohesion: 0.21
Nodes (4): AgyMesh, Path, Facade over session primitives, orchestration and administration., Mesh-check leg run by a worker: post PINGs, reply with their ids, do NOT wait.

### Community 13 - "Shared TODO Board"
Cohesion: 0.11
Nodes (6): Path, Atomically take a task (the given one, or the oldest open one). None = nothing…, TaskBoard, BoardOpsMixin, Needs ``self.board`` (TaskBoard) and ``self.journal``; registers its ops in…, TestTaskBoard

### Community 14 - "Hub Router Ops"
Cohesion: 0.10
Nodes (8): RateGate, ``requests_per_minute`` refill rate with a ``burst_size`` bucket per sender., HubRouter, Called by the server when a recv answer could not be written: requeue the…, Dispatches one request dict to its handler and always answers with ``{"ok":…, TestRateGate, fixture, router()

### Community 15 - "hub registry and models"
Cohesion: 0.15
Nodes (6): Thread-safe name -> SessionInfo map; a session unseen for ``stale_after_s`` is…, SessionRegistry, A joined agy session, the analog of Claude's ``~/.claude/sessions/<pid>.json``., SessionInfo, Clock, TestSessionRegistry

### Community 16 - "Process Tree Origin (part 2)"
Cohesion: 0.14
Nodes (8): AdminMixin, Path, Operations that set the mesh up; they may run from any terminal., Operations that set the mesh up; they may run from any terminal., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port., Open agy windows. ``ping_test``: the master runs the PING/PONG check after…, Block until ``count`` workers (default: the whole team) have joined; returns…

### Community 17 - "art AGY"
Cohesion: 0.10
Nodes (35): TaskBoard (shared TODO board), art agent (visual artist), joke agent (Hebrew humorist), poem agent (Hebrew 4-line poet), Blocking wait listen loop, examples/creative-trio/README.md (document), examples/creative-trio/art/AGY.md (document), examples/creative-trio/joke/AGY.md (document) (+27 more)

### Community 18 - "_src build"
Cohesion: 0.60
Nodes (5): add_watermarks(), assemble(), inline_images(), main(), validate()

### Community 19 - "Hub Journal"
Cohesion: 0.40
Nodes (3): Journal, Path, Append-only JSON-lines log of joins and messages (for debugging and teaching).

### Community 26 - "CLI Handlers & Errors (part 4)"
Cohesion: 0.20
Nodes (4): Outcome of one request: the reply message, or why there is none., Reply, reply(), TestRenderer

### Community 29 - "CLI Handlers & Errors (part 2)"
Cohesion: 0.23
Nodes (6): _default_opener(), Path, One ``dir="auto"`` block PER LINE: each line takes its direction from its own…, ResultWriter, slug(), TestResultWriter

### Community 32 - "Hub TCP Server (part 2)"
Cohesion: 0.24
Nodes (7): ProtocolError, A frame on the wire is not valid JSON or is too large., LineChannel, socket, One JSON object per line, UTF-8, never more than ``max_bytes`` per frame., Return the next frame, or None when the peer closed the connection., TestLineChannel

### Community 34 - "Mesh Check & Orchestration (part 2)"
Cohesion: 0.21
Nodes (6): MeshChecker, MeshReport, parse_sent(), ``{"sent": {peer: ping_id}}`` from a peer's meshcheck reply; {} if malformed., FakeOrch, TestMeshChecker

### Community 35 - "Hub Client Gatekeeper (part 2)"
Cohesion: 0.31
Nodes (3): Orchestrator, Sender side of the mesh, used by the master and by workers running ``ping-all``., Wait for the replies to any request ids (``key -> id``) under one shared…

### Community 37 - "master AGY and USER MANUAL"
Cohesion: 0.11
Nodes (30): CRITICAL DIRECTIVES (delegate, no exploration, one command), dispatch-all single-command fan-out, Exploration overhead (PRD failure 2), Speed rules (foreground, think briefly), docs/USER_MANUAL.md (document), examples/creative-trio/master/AGY.md (document), src/agymesh/templates/master.md (document), 1. The idea in five sentences (+22 more)

### Community 41 - "poem AGY"
Cohesion: 0.42
Nodes (8): examples/creative-trio/poem/AGY.md (document), AGY Mesh Agent: `poem`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub), Speed rules

## Knowledge Gaps
- **3 isolated node(s):** `agymesh`, `setup-git.sh script`, `Corrections / additions (for the report)`
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgyMesh` connect `Mesh Check & Orchestration (part 4)` to `agymesh errors`, `Mesh Check & Orchestration (part 2)`, `agymesh models`, `Mesh Check & Orchestration`, `CLI Parser & Commands`, `Hub Client Gatekeeper (part 2)`, `Mailbox Store`, `Hub Client Gatekeeper`, `Config & Team Loading`, `Mesh Check & Orchestration (part 3)`, `Integration Test Fixtures`, `Process Tree Origin (part 2)`, `CLI Handlers & Errors (part 4)`, `CLI Handlers & Errors (part 2)`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `MeshError` connect `agymesh errors` to `Hub TCP Server (part 2)`, `agymesh models`, `Config & Team Loading`, `Hub Client Gatekeeper`, `Hub Client Gatekeeper (part 2)`, `CLI Parser & Commands`, `Mailbox Store`, `Process Tree Origin`, `Integration Test Fixtures`, `Hub TCP Server`, `test launcher instructions`, `Mesh Check & Orchestration (part 4)`, `Shared TODO Board`, `Hub Router Ops`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `Message` connect `Mailbox Store` to `agymesh errors`, `agymesh models`, `Hub Client Gatekeeper (part 2)`, `Mesh Check & Orchestration`, `Hub Client Gatekeeper`, `Mesh Check & Orchestration (part 2)`, `test launcher instructions`, `Mesh Check & Orchestration (part 4)`, `CLI Handlers & Errors (part 4)`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Message` (e.g. with `Orchestrator` and `Reply`) actually correct?**
  _`Message` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MeshError` (e.g. with `HubClient` and `TerminalLauncher`) actually correct?**
  _`MeshError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `AgyMesh` (e.g. with `MeshError` and `MeshChecker`) actually correct?**
  _`AgyMesh` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Reply` (e.g. with `Message` and `Renderer`) actually correct?**
  _`Reply` has 8 INFERRED edges - model-reasoned connections that need verification._