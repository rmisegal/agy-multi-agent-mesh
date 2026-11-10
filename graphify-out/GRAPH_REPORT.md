# Graph Report - Multi-Agent-Mesh  (2026-11-10)

## Corpus Check
- Corpus is ~27,172 words - fits in a single context window. You may not need a graph.

## Summary
- 618 nodes · 1403 edges · 26 communities (24 shown, 2 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.92)
- Token cost: 99,944 input · 0 output

## Community Hubs (Navigation)
- Mesh Concepts & Lessons
- CLI Handlers & Errors
- Config & Team Loading
- Hub Client Gatekeeper
- Mesh Check & Orchestration
- CLI Parser & Commands
- Agent Launch & Specs
- Mailbox Store
- Process Tree Origin
- Integration Test Fixtures
- Hub TCP Server
- Hub Autostart Launcher
- AGY.md Instruction Writer
- Shared TODO Board
- Hub Router Ops
- Data Models
- Rate Gate
- Session Registry
- Board Hub Ops
- Hub Journal
- Package Root

## God Nodes (most connected - your core abstractions)
1. `Message` - 46 edges
2. `MeshError` - 44 edges
3. `AgyMesh` - 39 edges
4. `Reply` - 38 edges
5. `HubClient` - 34 edges
6. `Handlers` - 28 edges
7. `MeshConfig` - 25 edges
8. `HubRouter` - 25 edges
9. `PLAN - agymesh 1.10` - 25 edges
10. `TaskBoard` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Speed rules (foreground, think briefly)` --semantically_similar_to--> `Exploration overhead (PRD failure 2)`  [INFERRED] [semantically similar]
  src/agymesh/templates/worker.md → docs/PRD.md
- `TestHubServer` --uses--> `HubClient`  [INFERRED]
  tests/unit/test_client_server.py → src/agymesh/client.py
- `mesh_factory()` --uses--> `MeshConfig`  [INFERRED]
  tests/conftest.py → src/agymesh/config.py
- `test_send_from_plain_terminal_is_refused()` --uses--> `MeshConfig`  [INFERRED]
  tests/integration/test_creative_trio.py → src/agymesh/config.py
- `TestHubClient` --uses--> `MeshConfig`  [INFERRED]
  tests/unit/test_client_server.py → src/agymesh/config.py

## Import Cycles
- 4-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/hub/router_board.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/server.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`

## Hyperedges (group relationships)
- **Hub request pipeline: client to router to stores** — client_hubclient, protocol_linechannel, server_hubserver, router_hubrouter, mailbox_mailboxstore, registry_sessionregistry, gate_rategate, hub_journal [EXTRACTED 1.00]
- **creative-trio dispatch round (master + art, poem, joke)** — examples_creative_trio_master_agy_md, examples_creative_trio_art_agy_md, examples_creative_trio_poem_agy_md, examples_creative_trio_joke_agy_md, concept_dispatch_all, orchestrate_orchestrator [EXTRACTED 1.00]
- **Hebrew-safe output pattern** — concept_english_only_chat, concept_per_line_dir_auto, results_resultwriter, src_agymesh_templates_worker, src_agymesh_templates_master [INFERRED 0.85]

## Communities (26 total, 2 thin omitted)

### Community 0 - "Mesh Concepts & Lessons"
Cohesion: 0.06
Nodes (74): TaskBoard (shared TODO board), HubClient (API gatekeeper), Delivery ack with requeue, art agent (visual artist), joke agent (Hebrew humorist), poem agent (Hebrew 4-line poet), agy -i boot prompt, Antigravity CLI (agy) (+66 more)

### Community 1 - "CLI Handlers & Errors"
Cohesion: 0.08
Nodes (19): Exception, HubUnavailableError, MeshError, ProtocolError, Base error of the mesh; ``code`` travels over the wire in hub replies., The hub is not running or cannot be reached., A frame on the wire is not valid JSON or is too large., new_id() (+11 more)

### Community 2 - "Config & Team Loading"
Cohesion: 0.06
Nodes (36): parametrize, check_version(), MeshConfig, Path, Read a JSON file (BOM tolerant) and raise ConfigError with the path when it…, Dotted-key access to the merged settings, with defaults as the only fallback., Resolve a path from the config relative to the project root., How an agy session invokes the CLI. Auto: the project's own ``.venv`` launcher… (+28 more)

### Community 3 - "Hub Client Gatekeeper"
Cohesion: 0.06
Nodes (19): HubClient, Stateless request/response client: one TCP connection per request., First attempt: if the hub is down and this is an agent op, start it once, retry., NotInSessionError, A mesh command was run from a plain terminal instead of from inside an agy…, Orchestrator, Sender side of the mesh, used by the master and by workers running ``ping-all``., Wait for the replies to any request ids (``key -> id``) under one shared… (+11 more)

### Community 4 - "Mesh Check & Orchestration"
Cohesion: 0.06
Nodes (13): MeshChecker, MeshReport, parse_sent(), ``{"sent": {peer: ping_id}}`` from a peer's meshcheck reply; {} if malformed., _one_line(), Renderer, AgyMesh, BoardMixin (+5 more)

### Community 5 - "CLI Parser & Commands"
Cohesion: 0.07
Nodes (12): ArgumentParser, Namespace, Handlers, parse_tasks(), main(), Hebrew output must not crash a cp1252 Windows console., utf8_console(), _board() (+4 more)

### Community 6 - "Agent Launch & Specs"
Cohesion: 0.11
Nodes (10): Opens one interactive agy session per agent, in the agent's own folder., TerminalLauncher, AgentSpec, One agent of a team: its folder, role and the template used by ``dispatch-all``., AdminMixin, Path, Operations that set the mesh up; they may run from any terminal., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port. (+2 more)

### Community 7 - "Mailbox Store"
Cohesion: 0.13
Nodes (8): MailboxStore, Thread-safe queues with max depth, overflow strategy and message time-to-live., Put back a message whose delivery failed (e.g. the agy tool call was killed)., Message, One envelope on the mesh. ``reply_to`` links a reply to the id of its request., TestMailboxStore, send(), TestHubRouter

### Community 8 - "Process Tree Origin"
Cohesion: 0.13
Nodes (11): _posix_snapshot(), snapshot(), _windows_snapshot(), Proc, ProcessTable, Snapshot of the process list with ancestor walks (cycle-safe: pids can be…, The outermost agy process above ``pid`` (agy may run helper agy children)., TerminalScanner (+3 more)

### Community 9 - "Integration Test Fixtures"
Cohesion: 0.12
Nodes (17): Event, slow, mesh_factory(), Build an AgyMesh client for a given fake agy pid, connected to the live hub., fixture, test_send_from_plain_terminal_is_refused(), trio(), worker_loop() (+9 more)

### Community 10 - "Hub TCP Server"
Cohesion: 0.11
Nodes (11): exclusive_socket(), HubServer, socket, A delivered message counts only after the client confirms it; else it is…, Accept loop + one worker thread per connection., LineChannel, socket, One JSON object per line, UTF-8, never more than ``max_bytes`` per frame. (+3 more)

### Community 11 - "Hub Autostart Launcher"
Cohesion: 0.15
Nodes (8): detached_kwargs(), HubLauncher, Path, Starts ``python -m agymesh hub`` detached; the exclusive port bind makes it…, Return True if THIS call started the hub, False if one was already running.…, FakeClient, Spawn, TestHubLauncher

### Community 12 - "AGY.md Instruction Writer"
Cohesion: 0.16
Nodes (11): InstructionWriter, Path, A whole team: one master plus any number of worker agents., TeamSpec, Path, fill(), Path, Read an answer file whatever wrote it: UTF-8, UTF-8 with BOM, or UTF-16… (+3 more)

### Community 13 - "Shared TODO Board"
Cohesion: 0.19
Nodes (4): Path, Atomically take a task (the given one, or the oldest open one). None = nothing…, TaskBoard, TestTaskBoard

### Community 14 - "Hub Router Ops"
Cohesion: 0.14
Nodes (3): HubRouter, Called by the server when a recv answer could not be written: requeue the…, Dispatches one request dict to its handler and always answers with ``{"ok":…

### Community 15 - "Data Models"
Cohesion: 0.18
Nodes (6): DictMixin, Round-trip a dataclass through a JSON-safe dict, ignoring unknown keys., A joined agy session, the analog of Claude's ``~/.claude/sessions/<pid>.json``., SessionInfo, Clock, TestSessionRegistry

### Community 16 - "Rate Gate"
Cohesion: 0.24
Nodes (3): RateGate, ``requests_per_minute`` refill rate with a ``burst_size`` bucket per sender., TestRateGate

### Community 17 - "Session Registry"
Cohesion: 0.20
Nodes (4): Thread-safe name -> SessionInfo map; a session unseen for ``stale_after_s`` is…, SessionRegistry, fixture, router()

### Community 19 - "Hub Journal"
Cohesion: 0.33
Nodes (4): Journal, Path, Append-only JSON-lines log of joins and messages (for debugging and teaching)., test_journal_appends_json_lines()

## Knowledge Gaps
- **4 isolated node(s):** `agymesh`, `config/rate_limits.json`, `AdminMixin`, `terminals.py (agy processes to mesh names)`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgyMesh` connect `Mesh Check & Orchestration` to `CLI Handlers & Errors`, `Config & Team Loading`, `Hub Client Gatekeeper`, `CLI Parser & Commands`, `Agent Launch & Specs`, `Mailbox Store`, `Integration Test Fixtures`, `AGY.md Instruction Writer`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `MeshError` connect `CLI Handlers & Errors` to `Config & Team Loading`, `Hub Client Gatekeeper`, `Mesh Check & Orchestration`, `CLI Parser & Commands`, `Agent Launch & Specs`, `Mailbox Store`, `Integration Test Fixtures`, `AGY.md Instruction Writer`, `Shared TODO Board`, `Hub Router Ops`, `Rate Gate`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `Message` connect `Mailbox Store` to `CLI Handlers & Errors`, `Hub Client Gatekeeper`, `Mesh Check & Orchestration`, `Agent Launch & Specs`, `AGY.md Instruction Writer`, `Data Models`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Message` (e.g. with `Orchestrator` and `Reply`) actually correct?**
  _`Message` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MeshError` (e.g. with `HubClient` and `TerminalLauncher`) actually correct?**
  _`MeshError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `AgyMesh` (e.g. with `MeshError` and `MeshChecker`) actually correct?**
  _`AgyMesh` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Reply` (e.g. with `Message` and `Renderer`) actually correct?**
  _`Reply` has 8 INFERRED edges - model-reasoned connections that need verification._