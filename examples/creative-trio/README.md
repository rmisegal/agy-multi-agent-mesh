# Example team: creative-trio (master + art, poem, joke)

© 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.

| Folder | Agent | Role (from `team.json`) |
|---|---|---|
| `master/` | master | splits the goal, delegates, never writes content itself |
| `art/` | art | ASCII art (≤ 20 lines) or a vivid visual description |
| `poem/` | poem | exactly 4 rhyming lines in Hebrew |
| `joke/` | joke | one short, sharp Hebrew joke |

`team.json` is the single source of truth. Each folder's `AGY.md` is **generated** from it
(`uv run agymesh init`, also done by `up`) — edit `team.json`, not `AGY.md`. The committed
`AGY.md` files use the portable command `agymesh`; `up`/`init` rewrite them with the exact
command for your installation.

Run it:

```powershell
uv run agymesh up --with-master
```

Then, in the master window:

| Type | Expect |
|---|---|
| `check the mesh` | 3 × PONG, each "answered by agy pid …" |
| `run the full mesh-check` | "Full mesh: all 12 links work." |
| `חלק את הנושא "חורף ישראלי" לשלושת הסוכנים ברשת והצג את התוצאה המאוחדת.` | browser tab with art, poem and joke |
| `Put 4 haiku tasks on the board (one per season), then have poem and joke work the board.` | `todo-list` shows all 4 done, split between poem and joke |

Measured on the reference PC (Gemini Flash, effort low): dispatch-all ≈ 20–30 s, mesh-check ≈ 45 s.
