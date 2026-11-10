# agymesh — session-to-session messaging for Antigravity CLI (`agy`)

**Version 1.10** · © 2026 **Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd.**
All rights reserved — see [LICENSE](LICENSE).

`agymesh` lets several **interactive `agy` sessions**, each in its own window and folder, talk to
each other the way Claude Code sessions do with `ListAgents` / `SendMessage`: a master splits a
goal, sub-agents work in parallel, answers come back by message id. It is generic — agents,
roles and task templates come from a team file — and ships with a working example team
(master + art, poem, joke).

| Read this | For |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | installing on a student PC |
| [docs/USER_MANUAL.md](docs/USER_MANUAL.md) | how to use it: the example team, choosing the number of sub-agents, the shared TODO board, commands, troubleshooting |
| [examples/creative-trio/](examples/creative-trio/) | the master / art / poem / joke example |
| [docs/LESSONS.md](docs/LESSONS.md) | why the first design failed (24 lessons) |
| [docs/PLAN.md](docs/PLAN.md) | architecture, PRD coverage, quality audit |

## Quick start

```powershell
git clone https://github.com/rmisegal/agy-multi-agent-mesh.git
cd agy-multi-agent-mesh
uv sync
uv run agymesh up --with-master      # hub + AGY.md files + 4 agy windows
```

Answer agy's one-time "trust this folder" question in each window. Then type a goal in the
**master** window, e.g. `חלק את הנושא "חורף ישראלי" לשלושת הסוכנים והצג את התוצאה המאוחדת.`
The three workers answer in parallel and the merged result opens in your browser.

## How it works

```text
 agy "master"  ── dispatch ──►  hub 127.0.0.1:9877  ──► mailbox per agent ◄── wait ── agy "poem"
      ▲                        (registry · mailboxes ·                      ── reply ──►
      └──── replies by id ◄──── reply book · TODO board · journal)
```

* **The session does the talking.** A worker runs `agymesh wait`, which blocks until a message
  arrives, then answers with `agymesh reply`. Every message is stamped with the pid of the agy
  process that sent it; commands typed in a plain terminal are refused.
* **Robust transport.** Newline-framed JSON, replies matched by id, explicit `unknown_peer` errors,
  delivery acknowledgement with re-queue, per-agent FIFO mailboxes with TTL and overflow policy,
  per-sender rate gate.
* **Shared TODO board** in the hub with atomic `todo-claim` (no task is done twice).
* **Self-starting hub**, race-safe: random delay + exclusive port bind → exactly one hub.
* **Hebrew-safe output.** Chat is English-only (terminals cannot show RTL); results are saved as
  UTF-8 Markdown and per-line `dir="auto"` HTML and opened in the browser.

| Claude Code | agymesh |
|---|---|
| `~/.claude/sessions/<pid>.json` | `agymesh join` → hub registry (name, agy pid, folder) |
| `ListAgents` | `agymesh peers` |
| `SendMessage` | `agymesh send` / `dispatch` / `dispatch-all` |
| message delivered as a new turn | `agymesh wait` (blocking receive inside the session's turn) |
| `cli:mesh-communication` check | `agymesh ping-all`, `agymesh mesh-check` (parallel, full matrix) |

## Development

```powershell
uv run pytest            # 90 tests, coverage gate 85 % (currently 99 %)
uv run ruff check src tests
```

SDK-first (`from agymesh import AgyMesh`), no runtime dependencies, every Python file ≤ 150 code
lines, versioned config (`config/setup.json`, `config/rate_limits.json`, team files: `1.00`;
code: `1.10`). The project knowledge graph is in `graphify-out/` (stored gzipped in git; after
cloning run `bash scripts/setup-git.sh` then `git checkout -- graphify-out/graph.json`).

---

## התחלה מהירה (לסטודנטים)

1. התקנה: `git clone …`, `cd agy-multi-agent-mesh`, `uv sync` (פרטים ב-`docs/INSTALL.md`).
2. `uv run agymesh up --with-master` — פותח חלון `agy` לכל סוכן; כל סוכן מצטרף ומאזין **בעצמו**.
3. כתבו מטרה בחלון ה-master. הסוכנים עונים במקביל, והתוצאה נפתחת בדפדפן (עברית מימין לשמאל).
4. מספר תתי-הסוכנים = מספר הרשומות ב-`agents` בקובץ הצוות; רשימת משימות משותפת = לוח
   ה-TODO (`todo-add` / `todo-claim` / `todo-done`). הכול מוסבר ב-`docs/USER_MANUAL.md`.

© 2026 ד"ר יורם סגל, גל טכנולוגיות בינה מלאכותית בע"מ. כל הזכויות שמורות.
