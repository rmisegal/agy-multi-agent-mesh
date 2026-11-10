# OUTLINE — USER_MANUAL.md → animated Hebrew deck (12 slides)

Source: `docs/USER_MANUAL.md` (agymesh 1.11). The source is Markdown, not PPTX: each manual
section became one or two slides; no images existed, so every visual is code-drawn (HTML/SVG).

| # | Title | Source § | Visual | Build steps |
|---|-------|----------|--------|-------------|
| 1 | agymesh 1.11 – מדריך למשתמש | header | animated mesh: master → hub → art/poem/joke, flowing dots, rotating ring | entrance only |
| 2 | הרעיון בחמישה משפטים | §1 | architecture diagram (ASCII figure redrawn) | 1 agy windows · 2 hub + mailboxes + board · 3 wait loop · 4 you → master → dispatch → replies · 5 pid check, plain terminal refused |
| 3 | הצוות לדוגמה | §2 table | four role cards with sample outputs + folder tree | 1 master · 2 art · 3 poem · 4 joke · 5 folder tree |
| 4 | מהרצה ראשונה לתוצאה בדפדפן | §2 walk-through | terminal → master prompt → parallel bars → browser mock | 1 up · 2 status · 3 goal + dispatch-all · 4 parallel work 20–40 s · 5 browser result |
| 5 | עוד פקודות – ולמה הצ׳אט באנגלית | §2 tables + note | command table; reversed-Hebrew terminal vs browser | 1–4 table rows · 5 reversed terminal + reason · 6 browser + `.mesh/results/` |
| 6 | כמה סוכנים? קובץ הצוות | §3 | `team.json` panel, highlights, count-up, memory bar | 1 agents array = 4 · 2 `{topic}` substitution · 3 naming/folder rules · 4 `--team ... up` · 5 3–6 agents, ~250 MB each |
| 7 | תיבת דואר מול לוח משותף | §4 table | two side panels with mini diagrams | 1 mailbox · 2 board · 3 lock, atomic claim, persistence |
| 8 | הלוח בפעולה | §4 flow | kanban open/claimed/done, tasks move between columns | 1 todo-add · 2 dispatch "Work the board" · 3 atomic simultaneous claim · 4 done + next claim · 5 NO_OPEN_TASK + reply |
| 9 | תפעול יומיומי | §5 table | table, row groups highlighted | 1 install/start · 2 wait-peers/ping/hub · 3 monitor · 4 maintain · 5 stop · 6 manual opening |
| 10 | הפעלה אוטומטית של ה-hub | §5 auto start | 4 agents, random 0–3 s waits on a timeline, exclusive bind → one hub | 1 no hub · 2 random waits · 3 first binds · 4 others connect, 2nd bind fails · 5 4 → 1 |
| 11 | מי מריץ איזו פקודה | §6 | four role cards + global options | 1 you · 2 worker · 3 master · 4 any agy session · 5 global options |
| 12 | פתרון תקלות – ומה הלאה | §7 | table + closing "Full mesh" terminal | 1–5 rows · 6 closing emphasis |

## Corrections / additions (for the report)
- No factual corrections were needed.
- Added (illustrative, marked "דוגמה"): a sample ASCII cat, a 4-line Hebrew winter poem and a Hebrew joke on slide 3;
  a sample topic `src/login.py` for the `{topic}` substitution on slide 6; illustrative delay values
  (0.4 / 1.1 / 1.7 / 2.6 s) on slide 10; the arithmetic 6 × 250 MB ≈ 1.5 GB on slide 6;
  "12 links = 4 × 3 directed pairs" on slide 5.
- The closing slide repeats the manual's `mesh-check` success line as the closing emphasis.
