# User manual — agymesh 1.10

© 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.

Installation: see [INSTALL.md](INSTALL.md).

## 1. The idea in five sentences

1. Every agent is an ordinary, interactive **agy window** in its own folder, with its own `AGY.md`.
2. A small **hub** on your PC (`127.0.0.1:9877`) stores messages; it never answers for an agent.
3. A worker sits in a **listen loop**: it runs `agymesh wait`, which returns the moment a message
   arrives; it does the work and runs `agymesh reply`; then `wait` again.
4. The **master** splits your goal and sends the parts with ONE command (`dispatch-all` or
   `dispatch`); the answers come back by message id and open in your browser.
5. Every message carries the pid of the agy process that sent it — commands typed in a plain
   terminal are refused, so you always know the agents themselves did the talking.

```text
      you ──► master (agy) ── dispatch ──►  hub  ──► mailbox: art   ◄── wait ── art  (agy)
                   ▲                         │  ──► mailbox: poem  ◄── wait ── poem (agy)
                   └── replies by id ◄───────┘  ──► mailbox: joke  ◄── wait ── joke (agy)
                                             └── shared TODO board ◄─ todo-claim (any agent)
```

## 2. The example team: master + art, poem, joke

`examples/creative-trio/` contains four agent folders and one team file:

| Folder | Role | What it returns |
|---|---|---|
| `master/` | orchestrator: splits the goal, never writes content | one English summary line; the merged result opens in the browser |
| `art/` | visual artist | ASCII art (≤ 20 lines) or a vivid visual description |
| `poem/` | poet | exactly 4 rhyming lines in Hebrew |
| `joke/` | humorist | one short, sharp Hebrew joke |

Walk-through:

```powershell
uv run agymesh up --with-master      # 4 windows open; workers join and listen by themselves
uv run agymesh status                # art / poem / joke = listening
```

In the **master** window type a goal, e.g.:

> חלק את הנושא "חורף ישראלי" לשלושת הסוכנים ברשת והצג את התוצאה המאוחדת.

The master runs `agymesh dispatch-all --name master --topic "חורף ישראלי"`; each worker gets its
own task (from `task_template` in the team file), works in parallel and replies; a browser tab
opens with the three parts (Hebrew right-to-left, ASCII art left-to-right). Typical time: 20–40 s.

Other things to type in the master window:

| You type | The master runs | You get |
|---|---|---|
| "check the mesh" | `ping-all` | table: every peer answered PONG, from which agy pid, in how many seconds |
| "run the full mesh-check" | `mesh-check` | 4×4 matrix, "Full mesh: all 12 links work." |
| "ask only the poet for a poem about rain" | `send --to poem --text ...` | one answer |
| "art: a cat, joke: about cats" | `dispatch --to art=... --to joke=...` | custom split |

**Why the chat is English only:** Windows terminals cannot show right-to-left text, so Hebrew in
an agy window appears in reverse order. The agents therefore chat in English; Hebrew content goes
through the mesh untouched and is shown in the browser. Results are also saved in
`.mesh/results/` as `.md` and `.html`.

## 3. How many sub-agents? — the team file

The number of sub-agents is simply the number of entries in `agents` of the team file. Copy
`examples/creative-trio/team.json` to e.g. `teams/review/team.json` and edit it:

```json
{
  "version": "1.00",
  "name": "code-review",
  "master": {"name": "master", "folder": "master", "role": "Lead reviewer: splits and merges"},
  "agents": [
    {"name": "security", "folder": "security", "role": "Security reviewer",
     "instructions": "List vulnerabilities with file:line and a fix.",
     "task_template": "Review for security problems: {topic}"},
    {"name": "perf", "folder": "perf", "role": "Performance reviewer",
     "instructions": "List slow paths with file:line and a fix.",
     "task_template": "Review for performance problems: {topic}"},
    {"name": "style", "folder": "style", "role": "Style reviewer",
     "instructions": "List readability problems with file:line.",
     "task_template": "Review for readability: {topic}"},
    {"name": "tests", "folder": "tests", "role": "Test reviewer",
     "instructions": "List missing tests.",
     "task_template": "Find missing tests in: {topic}"}
  ]
}
```

Rules: names are lowercase letters/digits/`-`/`_`; folders are relative to the team file and are
created for you; `{topic}` in `task_template` is replaced by the master's topic.

```powershell
uv run agymesh --team teams/review/team.json up --with-master
```

To make it the default, set `"team_file"` in `config/setup.json`. `agymesh launch security perf`
opens only some of the agents. Practical limit: every agy window uses memory (~250 MB) and model
quota — 3 to 6 agents per PC is comfortable.

## 4. A shared TODO list — the board (and how it differs from the inbox)

| | **Mailbox ("inbox")** | **Shared TODO board** |
|---|---|---|
| Who sees it | only its owner | the whole team |
| What it holds | messages addressed to one agent | tasks anyone can take |
| Read with | `wait` (removes the message) | `todo-list` (read-only), `todo-claim` |
| Typical use | "poem, write X" | "here are 12 tasks — whoever is free takes the next one" |

So: no, a shared list does **not** use the inbox. The board lives in the hub, and every change
goes through it under a lock: **`todo-claim` is atomic** — two agents asking at the same moment
always get two different tasks (tested with 8 parallel agents). The board is saved to
`.mesh/board.json` after every change and survives a hub restart.

Commands (agents run them; `todo-list` and `todo-clear` work from any terminal):

```text
agymesh todo-add   --name master --title "task 1" --title "task 2" ...
agymesh todo-claim --name poem                 # -> CLAIMED T001: task 1   (or NO_OPEN_TASK)
agymesh todo-done  --name poem --id T001 --note "one-line result"
agymesh todo-list  [--status open|claimed|done]
agymesh todo-clear
```

Typical flow, typed in the master window:

> Put these on the board: a winter haiku, a summer haiku, a spring haiku, an autumn haiku.
> Then have poem and joke work the board.

The master runs `todo-add` (four `--title`s) and one `dispatch --to poem="Work the board"
--to joke="Work the board"`. Each worker loops `todo-claim` → work → `todo-done` until
`NO_OPEN_TASK`, then replies with the ids it completed. Watch progress any time:
`uv run agymesh todo-list`.

## 5. Everyday operation

| Task | Command (normal PowerShell, in the project folder) |
|---|---|
| start everything | `uv run agymesh up --with-master` |
| start only the hub | `uv run agymesh up --no-launch` (agents also start it automatically) |
| who is online | `uv run agymesh status` / `uv run agymesh peers` |
| which agy windows run | `uv run agymesh terminals` |
| regenerate AGY.md after editing the team file | `uv run agymesh init` |
| reopen one agent | `uv run agymesh launch poem` |
| stop | close the agy windows, then `uv run agymesh down` |

Opening an agent by hand instead of `up`: `cd examples\creative-trio\poem`, run `agy`, type
`start mesh`.

**Automatic hub start.** If the hub is not running, the first agent command (`join`, `wait`,
`send`, `reply`, board writes) starts it. When several agents do this at once, each waits a random
0–3 s and re-checks; and the hub binds its port exclusively, so even simultaneous starts end with
exactly ONE hub (tested: 4 agents at once → 1 hub).

## 6. Command reference

| Command | Run by | Purpose |
|---|---|---|
| `up [--no-launch] [--with-master]`, `hub`, `down`, `status`, `init`, `launch [names]`, `peers`, `terminals`, `todo-list`, `todo-clear` | you | setup and monitoring |
| `join`, `wait`, `reply --id ... --text/--file`, `leave` | worker agy session | listen loop |
| `send`, `dispatch --to p=task ...`, `dispatch-all --topic`, `ping-all`, `mesh-check` | master agy session | delegation and health |
| `todo-add`, `todo-claim`, `todo-done` | any agy session | shared board |

Global options: `--team <file>`, `--config-dir <folder>`, `--allow-external` (diagnostics only).

## 7. Troubleshooting

| Symptom | Meaning / fix |
|---|---|
| a peer shows `NO ANSWER` | it is busy on a long task, waiting on a prompt in its window, or not in its `wait` loop — look at its window; type `start mesh` there if it stopped |
| a turn takes ~60 s | the model service answered slowly (visible in agy's own log); nothing to fix locally |
| Hebrew reversed in an agy window | expected in terminals; read the result in the browser |
| `unknown_peer` | that agent never joined — check `status`, reopen it with `launch` |
| hub logs | `.mesh/journal.jsonl` (every join, message and board change, with timestamps) |

More background: [LESSONS.md](LESSONS.md) (why the first design failed) and [PLAN.md](PLAN.md).
