# Graph Report - mesh-pr  (2026-11-11)

## Corpus Check
- 73 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 789 nodes · 1762 edges · 44 communities (27 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 188 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `42e05836`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_PLAN|PLAN]]
- [[_COMMUNITY_CLI Parser & Commands (part 3)|CLI Parser & Commands (part 3)]]
- [[_COMMUNITY_Config & Team Loading|Config & Team Loading]]
- [[_COMMUNITY_Hub Router Ops (part 2)|Hub Router Ops (part 2)]]
- [[_COMMUNITY_Mesh Check & Orchestration|Mesh Check & Orchestration]]
- [[_COMMUNITY_CLI Parser & Commands|CLI Parser & Commands]]
- [[_COMMUNITY_PRD|PRD]]
- [[_COMMUNITY_Mailbox Store|Mailbox Store]]
- [[_COMMUNITY_Process Tree Origin|Process Tree Origin]]
- [[_COMMUNITY_Integration Test Fixtures|Integration Test Fixtures]]
- [[_COMMUNITY_hub server|hub server]]
- [[_COMMUNITY_test launcher instructions|test launcher instructions]]
- [[_COMMUNITY_Mesh Check & Orchestration (part 4)|Mesh Check & Orchestration (part 4)]]
- [[_COMMUNITY_Shared TODO Board|Shared TODO Board]]
- [[_COMMUNITY_Hub Router Ops|Hub Router Ops]]
- [[_COMMUNITY_hub registry and models|hub registry and models]]
- [[_COMMUNITY_Process Tree Origin (part 2)|Process Tree Origin (part 2)]]
- [[_COMMUNITY_art AGY|art AGY]]
- [[_COMMUNITY__src build|_src build]]
- [[_COMMUNITY_Integration Test Fixtures (part 2)|Integration Test Fixtures (part 2)]]
- [[_COMMUNITY_Package Root|Package Root]]
- [[_COMMUNITY_CLI Package|CLI Package]]
- [[_COMMUNITY_Hub Package|Hub Package]]
- [[_COMMUNITY_Tests Package|Tests Package]]
- [[_COMMUNITY_Integration Package|Integration Package]]
- [[_COMMUNITY_Unit Package|Unit Package]]
- [[_COMMUNITY_CLI Handlers & Errors (part 4)|CLI Handlers & Errors (part 4)]]
- [[_COMMUNITY__src OUTLINE|_src OUTLINE]]
- [[_COMMUNITY_art AGY (part 2)|art AGY (part 2)]]
- [[_COMMUNITY_CLI Handlers & Errors (part 2)|CLI Handlers & Errors (part 2)]]
- [[_COMMUNITY_Shared TODO Board (part 2)|Shared TODO Board (part 2)]]
- [[_COMMUNITY_agymesh launcher|agymesh launcher]]
- [[_COMMUNITY_CLI Parser & Commands (part 2)|CLI Parser & Commands (part 2)]]
- [[_COMMUNITY_Mesh Check & Orchestration (part 2)|Mesh Check & Orchestration (part 2)]]
- [[_COMMUNITY_Hub Client Gatekeeper (part 2)|Hub Client Gatekeeper (part 2)]]
- [[_COMMUNITY_master AGY and USER MANUAL|master AGY and USER MANUAL]]
- [[_COMMUNITY_poem AGY|poem AGY]]
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
- `Speed rules (foreground, think briefly)` --semantically_similar_to--> `Exploration overhead (PRD failure 2)`  [INFERRED] [semantically similar]
  src/agymesh/templates/worker.md → docs/PRD.md
- `test_send_from_plain_terminal_is_refused()` --uses--> `MeshError`  [INFERRED]
  tests/integration/test_creative_trio.py → src/agymesh/errors.py
- `TestTaskBoard` --uses--> `MeshError`  [INFERRED]
  tests/unit/test_board.py → src/agymesh/errors.py
- `test_parse_tasks()` --uses--> `MeshError`  [INFERRED]
  tests/unit/test_cli.py → src/agymesh/errors.py
- `TestTeamLoader` --uses--> `MeshError`  [INFERRED]
  tests/unit/test_config_team.py → src/agymesh/errors.py

## Import Cycles
- 4-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/router.py -> src/agymesh/hub/router_board.py -> src/agymesh/__init__.py`
- 5-file cycle: `src/agymesh/__init__.py -> src/agymesh/sdk.py -> src/agymesh/sdk_base.py -> src/agymesh/hub/server.py -> src/agymesh/hub/router.py -> src/agymesh/__init__.py`

## Hyperedges (group relationships)
- **creative-trio dispatch round (master + art, poem, joke)** — examples_creative_trio_master_agy_md, examples_creative_trio_art_agy_md, examples_creative_trio_poem_agy_md, examples_creative_trio_joke_agy_md, concept_dispatch_all, orchestrate_orchestrator [EXTRACTED 1.00]
- **Hub request pipeline: client to router to stores** — client_hubclient, protocol_linechannel, server_hubserver, router_hubrouter, mailbox_mailboxstore, registry_sessionregistry, gate_rategate, hub_journal [EXTRACTED 1.00]
- **Hebrew-safe output pattern** — concept_english_only_chat, concept_per_line_dir_auto, results_resultwriter, src_agymesh_templates_worker, src_agymesh_templates_master [INFERRED 0.85]

## Communities (44 total, 17 thin omitted)

### Community 0 - "PLAN"
Cohesion: 0.06
Nodes (74): HubClient (API gatekeeper), Delivery ack with requeue, Antigravity CLI (agy), Claude Code ListAgents/SendMessage analogy, English-only chat language rule, Fake PONG daemon shortcut (PRD failure 3), Hub-and-spoke localhost TCP topology, Race-safe hub autostart (jitter + exclusive bind) (+66 more)

### Community 1 - "CLI Parser & Commands (part 3)"
Cohesion: 0.33
Nodes (8): ArgumentParser, main(), Hebrew output must not crash a cp1252 Windows console., utf8_console(), _board(), build_parser(), _name(), The shared TODO board (one list for the whole team, kept by the hub).

### Community 2 - "Config & Team Loading"
Cohesion: 0.06
Nodes (38): parametrize, check_version(), MeshConfig, Path, Read a JSON file (BOM tolerant) and raise ConfigError with the path when it…, Dotted-key access to the merged settings, with defaults as the only fallback., Resolve a path from the config relative to the project root., How an agy session invokes the CLI. Auto: the project's own ``.venv`` launcher… (+30 more)

### Community 3 - "Hub Router Ops (part 2)"
Cohesion: 0.18
Nodes (4): RateGate, ``requests_per_minute`` refill rate with a ``burst_size`` bucket per sender., Clock, TestRateGate

### Community 6 - "PRD"
Cohesion: 0.07
Nodes (55): agy -i boot prompt, CRITICAL DIRECTIVES (delegate, no exploration, one command), accept() blocks Ctrl+C (PRD failure 6), dispatch-all single-command fan-out, PowerShell ExecutionPolicy block (PRD failure 5), Exploration overhead (PRD failure 2), inbox.ipc / response.ipc file bridge (legacy), Master orchestrator role (+47 more)

### Community 7 - "Mailbox Store"
Cohesion: 0.07
Nodes (14): MailboxStore, Thread-safe queues with max depth, overflow strategy and message time-to-live., Put back a message whose delivery failed (e.g. the agy tool call was killed)., DictMixin, Message, Round-trip a dataclass through a JSON-safe dict, ignoring unknown keys., One envelope on the mesh. ``reply_to`` links a reply to the id of its request., Path (+6 more)

### Community 8 - "Process Tree Origin"
Cohesion: 0.10
Nodes (16): NotInSessionError, A mesh command was run from a plain terminal instead of from inside an agy…, _posix_snapshot(), snapshot(), _windows_snapshot(), OriginGuard, Proc, ProcessTable (+8 more)

### Community 9 - "Integration Test Fixtures"
Cohesion: 0.23
Nodes (14): slow, mesh_factory(), Build an AgyMesh client for a given fake agy pid, connected to the live hub., test_send_from_plain_terminal_is_refused(), test_board_through_cli_and_hub(), echo_worker(), poem(), fixture (+6 more)

### Community 10 - "hub server"
Cohesion: 0.05
Nodes (41): Starts ``python -m agymesh hub`` detached; the exclusive port bind makes it sing, Return True if THIS call started the hub, False if one was already running., bool, Exception, HubClient, Stateless request/response client: one TCP connection per request., First attempt: if the hub is down and this is an agent op, start it once, retry., HubUnavailableError (+33 more)

### Community 11 - "test launcher instructions"
Cohesion: 0.06
Nodes (25): AgentSpec, Open the window OUTSIDE the caller's job object when that is allowed.          a, int, InstructionWriter, Path, Opens one interactive agy session per agent, in the agent's own folder., TerminalLauncher, AgentSpec (+17 more)

### Community 12 - "Mesh Check & Orchestration (part 4)"
Cohesion: 0.21
Nodes (4): AgyMesh, Path, Facade over session primitives, orchestration and administration., Mesh-check leg run by a worker: post PINGs, reply with their ids, do NOT wait.

### Community 13 - "Shared TODO Board"
Cohesion: 0.19
Nodes (4): Path, Atomically take a task (the given one, or the oldest open one). None = nothing…, TaskBoard, TestTaskBoard

### Community 14 - "Hub Router Ops"
Cohesion: 0.14
Nodes (3): HubRouter, Called by the server when a recv answer could not be written: requeue the…, Dispatches one request dict to its handler and always answers with ``{"ok":…

### Community 15 - "hub registry and models"
Cohesion: 0.18
Nodes (4): Thread-safe name -> SessionInfo map; a session unseen for ``stale_after_s`` is…, SessionRegistry, fixture, router()

### Community 16 - "Process Tree Origin (part 2)"
Cohesion: 0.14
Nodes (8): AdminMixin, Path, Operations that set the mesh up; they may run from any terminal., Operations that set the mesh up; they may run from any terminal., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port., Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port., Open agy windows. ``ping_test``: the master runs the PING/PONG check after…, Block until ``count`` workers (default: the whole team) have joined; returns…

### Community 17 - "art AGY"
Cohesion: 0.13
Nodes (29): TaskBoard (shared TODO board), art agent (visual artist), joke agent (Hebrew humorist), poem agent (Hebrew 4-line poet), Blocking wait listen loop, examples/creative-trio/README.md (document), examples/creative-trio/joke/AGY.md (document), src/agymesh/templates/worker.md (document) (+21 more)

### Community 18 - "_src build"
Cohesion: 0.60
Nodes (5): add_watermarks(), assemble(), inline_images(), main(), validate()

### Community 19 - "Integration Test Fixtures (part 2)"
Cohesion: 0.20
Nodes (4): Event, fixture, trio(), worker_loop()

### Community 26 - "CLI Handlers & Errors (part 4)"
Cohesion: 0.20
Nodes (4): Outcome of one request: the reply message, or why there is none., Reply, reply(), TestRenderer

### Community 28 - "art AGY (part 2)"
Cohesion: 0.42
Nodes (9): examples/creative-trio/art/AGY.md (document), art/AGY.md, AGY Mesh Agent: `art`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub) (+1 more)

### Community 29 - "CLI Handlers & Errors (part 2)"
Cohesion: 0.23
Nodes (6): _default_opener(), Path, One ``dir="auto"`` block PER LINE: each line takes its direction from its own…, ResultWriter, slug(), TestResultWriter

### Community 31 - "agymesh launcher"
Cohesion: 0.50
Nodes (3): float, HubClient, Path

### Community 34 - "Mesh Check & Orchestration (part 2)"
Cohesion: 0.16
Nodes (6): MeshChecker, MeshReport, parse_sent(), ``{"sent": {peer: ping_id}}`` from a peer's meshcheck reply; {} if malformed., FakeOrch, TestMeshChecker

### Community 35 - "Hub Client Gatekeeper (part 2)"
Cohesion: 0.36
Nodes (3): Orchestrator, Sender side of the mesh, used by the master and by workers running ``ping-all``., Wait for the replies to any request ids (``key -> id``) under one shared…

### Community 37 - "master AGY and USER MANUAL"
Cohesion: 0.42
Nodes (9): docs/USER_MANUAL.md (document), 1. The idea in five sentences, 2. The example team: master + art, poem, joke, 3. How many sub-agents? — the team file, 4. A shared TODO list — the board (and how it differs from the inbox), 5. Everyday operation, 6. Command reference, 7. Troubleshooting (+1 more)

### Community 41 - "poem AGY"
Cohesion: 0.42
Nodes (9): examples/creative-trio/poem/AGY.md (document), poem/AGY.md, AGY Mesh Agent: `poem`, Boot (once: when this session starts, or when the user types "start mesh"), Language rule (this terminal cannot show right-to-left text), Listen loop (repeat until the user in THIS window says "stop mesh"), Rules, Shared TODO board (one list for the whole team, kept by the hub) (+1 more)

## Knowledge Gaps
- **12 isolated node(s):** `agymesh`, `cli/__init__.py`, `hub/__init__.py`, `tests/__init__.py`, `integration/__init__.py` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MeshError` connect `hub server` to `CLI Parser & Commands (part 2)`, `CLI Parser & Commands (part 3)`, `Config & Team Loading`, `Hub Router Ops (part 2)`, `Hub Client Gatekeeper (part 2)`, `Mailbox Store`, `Process Tree Origin`, `Integration Test Fixtures`, `test launcher instructions`, `Mesh Check & Orchestration (part 4)`, `Shared TODO Board`, `Hub Router Ops`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `AgyMesh` connect `Mesh Check & Orchestration (part 4)` to `CLI Parser & Commands (part 3)`, `Mesh Check & Orchestration (part 2)`, `Hub Client Gatekeeper (part 2)`, `Mesh Check & Orchestration`, `Config & Team Loading`, `Mailbox Store`, `Integration Test Fixtures`, `hub server`, `test launcher instructions`, `Mesh Check & Orchestration (part 3)`, `Process Tree Origin (part 2)`, `CLI Handlers & Errors (part 4)`, `CLI Handlers & Errors (part 2)`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `Message` connect `Mailbox Store` to `Mesh Check & Orchestration (part 2)`, `Hub Client Gatekeeper (part 2)`, `Mesh Check & Orchestration`, `hub server`, `Mesh Check & Orchestration (part 4)`, `CLI Handlers & Errors (part 4)`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Message` (e.g. with `Orchestrator` and `Reply`) actually correct?**
  _`Message` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MeshError` (e.g. with `HubClient` and `TerminalLauncher`) actually correct?**
  _`MeshError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `AgyMesh` (e.g. with `MeshError` and `MeshChecker`) actually correct?**
  _`AgyMesh` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Reply` (e.g. with `Message` and `Renderer`) actually correct?**
  _`Reply` has 8 INFERRED edges - model-reasoned connections that need verification._