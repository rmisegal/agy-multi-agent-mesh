# מסמך אפיון ודרישות מערכת (PRD): רשת תקשורת מבוזרת בין מופעי Antigravity CLI (AGY Mesh)

**גרסה:** 2.0 (מהדורה מאוחדת ומלאה)  
**תאריך:** נובמבר 2026  
**סביבת יעד:** Windows / PowerShell / Python 3.x / Antigravity CLI (`agy`)  
**נתיב פרויקט ראשי:** `D:\27D\UOH\UOH-AI-IMP\L04`

---

## 1. תקציר מנהלים ומטרת העל (Executive Summary & Core Objective)

### 1.1 מטרת הפרויקט
מטרת הפרויקט היא לתכנן, להקים ולהפעיל ארכיטקטורת **Multi-Agent Mesh** מקומית, שבה מספר תהליכי CLI עצמאיים של **Antigravity (`agy`)** מתקשרים זה עם זה בזמן אמת, מחלקים ביניהם עבודה ופועלים כנחיל (Swarm/Cluster) מתואם.

### 1.2 תרחיש הייחוס (Reference Use Case)
המשתמש מזין משימת-על בשפה טבעית לסוכן ראשי אחד בלבד (**Master Orchestrator**) – לדוגמה: *"תן ביטוי יצירתי ועשיר לנושא חורף ישראלי"*.
1. **האורקסטרטור (Master AGY):** מנוע מלייצר את התוכן היצירתי בעצמו. תפקידו לנתח את הבקשה, לפרק אותה לתתי-משימות מותאמות, ולשגר אותן במקביל דרך רשת תקשורת מקומית (IPC/TCP) לשלושה סוכני משנה מתמחים.
2. **סוכני המשנה (Sub-Agents):** שלושה מופעי `agy` נפרדים הרצים בתיקיות ייעודיות:
   * **`art`:** אחראי על יצירת תיאור ויזואלי עשיר או אומנות ASCII.
   * **`poem`:** אחראי על כתיבת שיר קצר ומחורז בן 4 שורות בעברית.
   * **`joke`:** אחראי על כתיבת בדיחה קצרה, שנונה ומושחזת בעברית.
3. **איסוף וסינתזה (Synchronization & Synthesis):** סוכני המשנה מעבדים את המשימות **בתוך סשן ה-AGY שלהם**, מחזירים את התוצרים לאורקסטרטור, והאורקסטרטור מאחד אותם לפלט מעוצב ומוגמר על מסך המשתמש.

---

## 2. השוואת מימוש: Claude Code CLI לעומת Antigravity CLI (`agy`)

הצורך המרכזי בפרויקט נבע מהרצון לשחזר יכולות תזמור סוכנים המוכרות מסביבת Claude Code בתוך סביבת Antigravity (`agy`), תוך התמודדות עם ההבדלים המבניים בין שני הכלים:

| מאפיין | Claude Code CLI | Antigravity CLI (`agy`) | משמעות ארכיטקטונית במימוש שלנו |
| :--- | :--- | :--- | :--- |
| **קובץ הנחיות מערכת** | `CLAUDE.md` | `AGY.md` | כל תיקיית סוכן חייבת להכיל קובץ `AGY.md` המגדיר את גבולות הגזרה, הזהות והפרוטוקול שלו. |
| **תת-סוכנים פנימיים** | תמיכה מובנית ב-Sub-agents / Task Spawning בתוך אותו תהליך. | סשנים נפרדים ועצמאיים בטרמינל ללא אפיק תקשורת משותף מובנה. | חובה לבנות שכבת תיווך חיצונית (**Mesh Hub + IPC Files**) שמגשרת בין תהליכי `agy` נפרדים. |
| **מודל הפעלה (REPL)** | תומך בהרצת משימות רקע ואינטראקציה רציפה. | פועל כ-REPL אינטראקטיבי פסיבי הממתין לקלט משתמש (אלא אם הופעל בלולאת פקודות או ב-Headless). | אם סשן `agy` פתוח בטרמינל ללא פקודה פעילה, הוא **לא יקרא מעצמו** קובצי `inbox.ipc` עד שייכנס ללולאת האזנה יזומה בתוך ה-AGY או יופעל דרך CLI trigger. |
| **נטייה לחקירת סביבה (Exploration)** | ממוקד מטרה לפי הוראות. | נטייה חזקה לבצע סריקות דיסק (`dir`, `Get-ChildItem`), קריאת קבצים וניתוח תהליכים לפני ביצוע. | חובה להטמיע ב-`AGY.md` איסורים מפורשים (**CRITICAL DIRECTIVES**) המונעים סריקות מיותרות וכופים הרצת פקודה יחידה. |

---

## 3. ארכיטקטורת המערכת (System Architecture)

### 3.1 טופולוגיית הרשת ומבנה התיקיות
המערכת מבוססת על טופולוגיית כוכב (Hub-and-Spoke) מעל TCP Sockets מקומיים (`127.0.0.1:9876`) בשילוב גשר קבצים (File-based IPC) בתיקיית כל סוכן.

```text
D:\27D\UOH\UOH-AI-IMP\L04\                  <-- תיקיית האורקסטרטור הראשי (Master AGY)
│   AGY.md                                  <-- הנחיות Master (חובת האצלה, איסור יצירה עצמית)
│   mesh_hub.py                             <-- שרת ה-TCP המרכזי + גשר ה-Daemon + כלי ה-CLI
│   bootstrap_agent.py                      <-- סקריפט עזר לרישום והרמת תשתית
│   update-agents-agy.ps1                   <-- סקריפט ליצירה/עדכון של קובצי AGY.md לסוכני המשנה
│   start-mesh-agents.ps1                   <-- סקריפט להרמת ה-Hub וה-Daemons ברקע
│   restart-agy-cluster.ps1                 <-- סקריפט איפוס מלא, הרמת תשתית ופתיחת טרמינלים
│
└───3-agents\
    ├───art\
    │       AGY.md                          <-- הגדרות סוכן אומנות / ASCII
    │       inbox.ipc                       <-- קובץ משימה נכנסת (נוצר ע"י ה-Daemon)
    │       response.ipc                    <-- קובץ תשובה יוצאת (נכתב ע"י ה-AGY)
    ├───poem\
    │       AGY.md                          <-- הגדרות סוכן שירה
    │       inbox.ipc
    │       response.ipc
    └───joke\
            AGY.md                          <-- הגדרות סוכן הומור
            inbox.ipc
            response.ipc
```

### 3.2 זרימת הנתונים מקצה לקצה (Data Flow Lifecycle)
1. **אתחול (Boot):** שרת `mesh_hub.py hub` עולה ומאזין בפורט `9876`.
2. **חיבור גשרים (Daemons):** עבור כל סוכן (`art`, `poem`, `joke`), עולה תהליך רקע `mesh_hub.py daemon` שמתחבר ב-Socket ל-Hub ומקשר אותו לתיקיית הסוכן.
3. **שיגור (Dispatch):** ה-Master AGY מקבל נושא מהמשתמש ומריץ פקודה אחת: `python mesh_hub.py dispatch-all --topic "<TOPIC>"`.
4. **הזרמה לדיסק:** ה-Hub מעביר את ההודעות ל-Daemons של הסוכנים. כל Daemon כותב את ההודעה לקובץ `inbox.ipc` בתיקיית הסוכן שלו.
5. **עיבוד בתוך ה-AGY (קריטי!):** מופע ה-`agy` של סוכן המשנה מזהה את `inbox.ipc`, קורא את התוכן (בין אם זה `PING` ובין אם זו משימה יצירתית), מבצע אותה **בתוך מוח ה-AGY**, וכותב את הפלט לקובץ `response.ipc`.
6. **איסוף (Gather):** ה-Daemon מזהה ש-`response.ipc` נוצר על ידי ה-AGY, קורא את התוכן, משדר אותו חזרה ב-Socket אל ה-Hub/Orchestrator, ומוחק את `inbox.ipc` ו-`response.ipc` לניקוי השטח.
7. **הצגה (Synthesis):** ה-Master AGY מקבל את שלוש התשובות המוכנות ומדפיס אותן במבנה מאוחד למשתמש.

---

## 4. ניתוח כשלים, בעיות שלמדנו בדרך והפתרונות שלהן (Post-Mortem & Lessons Learned)

במהלך הפיתוח והבדיקות נתקלנו ב-6 כשלים מהותיים. להלן תיעוד מדויק של כל כשל והפתרון ההנדסי שלו:

### כשל 1: האורקסטרטור מבצע את המשימה בעצמו במקום להאציל (Self-Generation Bypass)
* **התופעה:** כאשר התבקש ה-Master לתת ביטוי ל"חורף ישראלי", הוא כתב פואמה ארוכה בעצמו תוך 9 שניות והתעלם לחלוטין מסוכני המשנה.
* **הסיבה:** מודלי שפה מתוכנתים לענות מיד לבקשות יצירתיות אם אין איסור מפורש ומוחלט ב-System Prompt.
* **הפתרון:** הוספת בלוק `CRITICAL OPERATIONAL DIRECTIVES` ב-`L04\AGY.md` האוסר עליו בתכלית האיסור לייצר תוכן בעצמו ומחייב אותו להפעיל אך ורק כלי שורת פקודה.

### כשל 2: השהיה של 20 דקות עקב "מסע חקירה" (Exploration & Tool-Calling Overhead)
* **התופעה:** האורקסטרטור הריץ עשרות פקודות סרק (`dir`, `Get-ChildItem -Recurse`, `Get-Process`, קריאת 7 קבצים שונים, שליחת הודעת `"test"` בודדת ל-`art`) ודגם קבצים בלולאות איטיות של ה-LLM.
* **הסיבה:** כשה-Master מתבקש לנהל בעצמו 3 קריאות `send` נפרדות ואז לבדוק קבצים בלולאה, כל איטרציה דורשת קריאת API למודל וחשיבה (`Thought`), מה שמצטבר לדקות ארוכות.
* **הפתרון:**
  1. איחוד כל השיגור וההמתנה לפקודת Python מקומית ומהירה אחת: `dispatch-all`.
  2. הוספת איסור מפורש ב-`AGY.md` על הרצת `dir`, `Get-ChildItem`, או קריאת קובצי קוד מקומיים.

### כשל 3: מענה PING/PONG מזויף מחוץ ל-AGY (Daemon Shortcut Fallacy)
* **התופעה:** בגרסה הראשונה, תהליך ה-Daemon בפייתון יירט הודעות `"PING"` והחזיר `"PONG"` בעצמו ב-`0ms`. כתוצאה מכך, טבלת ה-`ping-all` הראתה שכולם `Reachable`, אך בפועל סשני ה-`agy` עצמם לא היו מחוברים למעגל העבודה ולא הגיבו למשימות אמת.
* **הסיבה:** הלוגיקה בוצעה בפייתון "מאחורי הגב" של ה-AGY במקום לעבור דרך קובצי ה-IPC אל הסוכן עצמו.
* **הפתרון:** הסרת המעקף מ-`run_daemon`. כל הודעה – **כולל PING** – נכתבת ל-`inbox.ipc`, וה-Daemon מחכה שה-**AGY בעצמו** יכתוב את התשובה ל-`response.ipc`.

### כשל 4: פסיביות של סשן ה-CLI בטרמינלים הפתוחים (Passive REPL Bottleneck)
* **התופעה:** פתחנו 3 חלונות PowerShell עם `agy` עבור `art`, `poem` ו-`joke`. הקובץ `inbox.ipc` נוצר בתיקייה, אך בחלון ה-`agy` שום דבר לא קרה.
* **הסיבה:** פקודת `agy` ללא פרמטרים פותחת שורת קלט אינטראקטיבית שמחכה להקלדת משתמש. הסוכן לא מריץ מעצמו תהליך רקע (Polling) כל עוד לא ניתנה לו פקודה ראשונית להיכנס ללולאת ניטור, או לחלופין הופעל עם פרומפט ישיר.
* **הפתרון הכפול:**
  * **למצב חלונות פתוחים (Interactive Watch):**בעת פתיחת החלון, מזריקים ל-`agy` פקודת התחלה המכניסה אותו ללולאת בדיקה רציפה של `inbox.ipc`.
  * **למצב אוטונומי מובטח (Guaranteed Execution):** הוספת מנגנון ב-Daemon או בלולאת הטרמינל שמעיר את `agy` מיד עם הופעת `inbox.ipc`.

### כשל 5: חסימת סקריפטים ב-PowerShell (`ExecutionPolicy` & `Zone.Identifier`)
* **התופעה:** הרצת `.\start-mesh-agents.ps1` נכשלה עם שגיאת `not digitally signed`, גם לאחר הרצת `Set-ExecutionPolicy RemoteSigned`.
* **הסיבה:** קבצים שנוצרים או מורדים מסומנים על ידי Windows ב-Stream חיצוני, ולעיתים מדיניות ה-Process דורסת את מדיניות המשתמש.
* **הפתרון:** שימוש ב-`Unblock-File` והרצה באמצעות:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\<script>.ps1`.

### כשל 6: תקיעת שרת ה-Hub בלחיצה על `Ctrl+C`
* **התופעה:** פקודת `server.accept()` ב-Socket חוסמת את ה-Thread הראשי ב-Windows ומונעת תפיסה של `KeyboardInterrupt`.
* **הפתרון:** הגדרת `server.settimeout(1.0)` בתוך לולאת ה-Hub, המאפשרת יציאה נקייה ומיידית בלחיצה על `Ctrl+C`.

---

## 5. מפרט הקוד והתצורה המלא (Full Implementation Reference)

להלן כל קובצי המערכת המלאים והסופיים שישמשו כתשתית הפרויקט.

### 5.1 קובץ הליבה: `mesh_hub.py`
קובץ זה כולל את ה-Hub, את ה-Daemon הנקי (שמעביר הכל דרך `inbox.ipc` ו-`response.ipc`), את בדיקת ה-`ping-all` האמיתית, ואת פקודת ה-`dispatch-all`.

```python
# mesh_hub.py - Central Mesh Hub & Pure IPC Bridge for Antigravity Agents
import argparse
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 9876

# Global registry of active sockets: { agent_name: socket }
agents = {}
lock = threading.Lock()


def handle_client(conn: socket.socket, addr):
    agent_name = None
    try:
        raw_reg = conn.recv(1024).decode("utf-8").strip()
        if not raw_reg:
            return
        msg = json.loads(raw_reg)
        if msg.get("type") == "REGISTER":
            agent_name = msg.get("name")
            with lock:
                agents[agent_name] = conn
            conn.sendall(json.dumps({"status": "OK"}).encode("utf-8") + b"\n")

            while True:
                line = conn.recv(8192)
                if not line:
                    break
                payload = json.loads(line.decode("utf-8").strip())
                dest = payload.get("to")
                with lock:
                    if dest in agents:
                        try:
                            agents[dest].sendall(line)
                        except Exception:
                            pass
    except Exception:
        pass
    finally:
        with lock:
            if agent_name and agent_name in agents:
                del agents[agent_name]
        conn.close()


def run_hub():
    """Starts the TCP Mesh Hub with 1s timeout for clean Ctrl+C exit."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(15)
    server.settimeout(1.0)
    print(f"[MESH-HUB] Active on {HOST}:{PORT}. Press Ctrl+C to stop.")

    try:
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(
                    target=handle_client, args=(conn, addr), daemon=True
                ).start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[MESH-HUB] Stopped cleanly by user.")
    finally:
        server.close()


def run_daemon(name: str, folder_path: str):
    """Pure IPC Bridge: Writes ALL incoming messages (including PING) to inbox.ipc.
    Waits for the AGY CLI session itself to write response.ipc, then sends it back.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        print(f"[{name}] Daemon failed to connect to Hub: {e}")
        sys.exit(1)

    s.sendall(json.dumps({"type": "REGISTER", "name": name}).encode("utf-8"))
    s.recv(1024)

    folder = Path(folder_path).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    inbox_file = folder / "inbox.ipc"
    response_file = folder / "response.ipc"

    print(f"[{name}] Daemon bridge active -> {folder}")

    while True:
        try:
            data = s.recv(8192)
            if not data:
                break
            msg = json.loads(data.decode("utf-8").strip())

            # 1. Remove stale response file if present
            if response_file.exists():
                try:
                    response_file.unlink()
                except Exception:
                    pass

            # 2. Write message to inbox.ipc for the AGY session
            inbox_file.write_text(json.dumps(msg, ensure_ascii=False), encoding="utf-8")

            # 3. Wait until AGY creates response.ipc with non-zero content
            while not (response_file.exists() and response_file.stat().st_size > 0):
                time.sleep(0.25)

            time.sleep(0.1)  # Grace period for file flush
            reply_text = response_file.read_text(encoding="utf-8").strip()

            # 4. Transmit AGY's response back over socket
            reply_msg = {
                "type": "MSG",
                "from": name,
                "to": msg.get("from"),
                "content": reply_text,
            }
            s.sendall(json.dumps(reply_msg).encode("utf-8") + b"\n")

            # 5. Clean up IPC files for next cycle
            for f in (inbox_file, response_file):
                if f.exists():
                    try:
                        f.unlink()
                    except Exception:
                        pass

        except Exception as e:
            print(f"[{name}] Daemon error: {e}")
            break
    s.close()


def ping_all(timeout: int = 20):
    """Sends PING to all peers and waits for the AGY sessions themselves to reply PONG."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    except Exception as e:
        print(f"Error: Unable to connect to Hub at {HOST}:{PORT} ({e})")
        sys.exit(1)

    s.sendall(json.dumps({"type": "REGISTER", "name": "orchestrator_ping"}).encode("utf-8"))
    s.recv(1024)

    peers = ["art", "poem", "joke"]
    print("| Peer | Ping Status | Response from AGY |")
    print("|---|---|---|")
    s.settimeout(timeout)
    for peer in peers:
        msg = {
            "type": "MSG",
            "from": "orchestrator_ping",
            "to": peer,
            "content": "PING",
        }
        try:
            s.sendall(json.dumps(msg).encode("utf-8") + b"\n")
            data = s.recv(8192)
            res = json.loads(data.decode("utf-8").strip())
            print(f"| {peer} | Reachable | {res.get('content')} |")
        except Exception:
            print(f"| {peer} | Unreachable | Timeout (Did AGY process inbox.ipc?) |")
    s.close()


def send_msg(to: str, msg_text: str, timeout: int = 45):
    """Sends a single message to a target agent and awaits AGY's reply."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    except Exception as e:
        print(f"Error: Unable to connect to Hub at {HOST}:{PORT} ({e})")
        sys.exit(1)

    s.sendall(json.dumps({"type": "REGISTER", "name": "sender_cli"}).encode("utf-8"))
    s.recv(1024)

    payload = {
        "type": "MSG",
        "from": "sender_cli",
        "to": to,
        "content": msg_text,
    }
    s.sendall(json.dumps(payload).encode("utf-8") + b"\n")
    print(f"[SENT] Dispatched to '{to}'. Waiting up to {timeout}s for AGY reply...")

    s.settimeout(timeout)
    try:
        data = s.recv(8192)
        res = json.loads(data.decode("utf-8").strip())
        print(f"\n--- [REPLY FROM {to.upper()}] ---")
        print(res.get("content"))
    except socket.timeout:
        print(f"[TIMEOUT] No reply from '{to}' within {timeout}s.")
    finally:
        s.close()


def dispatch_all(topic: str, timeout: int = 60):
    """Dispatches topic sub-tasks in parallel to art, poem, and joke and gathers responses."""
    tasks = {
        "art": f"Create an expressive ASCII art or vivid visual description for: {topic}",
        "poem": f"כתוב שיר מחורז בן 4 שורות בעברית על: {topic}",
        "joke": f"כתוב בדיחה קצרה ומושחזת בעברית על: {topic}",
    }

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(json.dumps({"type": "REGISTER", "name": "fast_orchestrator"}).encode("utf-8"))
        s.recv(1024)
        for agent, prompt in tasks.items():
            payload = {
                "type": "MSG",
                "from": "fast_orchestrator",
                "to": agent,
                "content": prompt,
            }
            s.sendall(json.dumps(payload).encode("utf-8") + b"\n")
    except Exception as e:
        print(f"Error connecting to Hub during dispatch: {e}")
        sys.exit(1)

    print(f"[ORCHESTRATOR] Dispatched tasks for topic: '{topic}'")
    print("[ORCHESTRATOR] Waiting for AGY sub-agents (art, poem, joke) to respond...")

    s.settimeout(timeout)
    responses = {}
    start_time = time.time()

    while len(responses) < len(tasks) and (time.time() - start_time < timeout):
        try:
            data = s.recv(8192)
            if not data:
                break
            msg = json.loads(data.decode("utf-8").strip())
            sender = msg.get("from")
            if sender in tasks:
                responses[sender] = msg.get("content", "")
                print(f"  [+] Received AGY response from: {sender}")
        except socket.timeout:
            break
        except Exception:
            break
    s.close()

    print("\n" + "=" * 60)
    print(f"      UNIFIED MESH SYNTHESIS: {topic}")
    print("=" * 60 + "\n")

    for agent in ["art", "poem", "joke"]:
        content = responses.get(agent, "[No response received / Timeout]")
        print(f"--- [{agent.upper()}] ---")
        print(content)
        print()


def cli():
    parser = argparse.ArgumentParser(description="Mesh Hub & IPC Bridge")
    parser.add_argument("action", choices=["hub", "daemon", "ping-all", "send", "dispatch-all"])
    parser.add_argument("--name", default="", help="Agent name")
    parser.add_argument("--folder", default=".", help="Agent folder")
    parser.add_argument("--to", default="", help="Target agent")
    parser.add_argument("--msg", default="", help="Message content")
    parser.add_argument("--topic", default="", help="Topic for dispatch-all")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    args = parser.parse_args()

    if args.action == "hub":
        run_hub()
    elif args.action == "daemon":
        run_daemon(args.name, args.folder)
    elif args.action == "ping-all":
        ping_all(args.timeout)
    elif args.action == "send":
        send_msg(args.to, args.msg, args.timeout)
    elif args.action == "dispatch-all":
        dispatch_all(args.topic, args.timeout)


if __name__ == "__main__":
    cli()
```

---

### 5.2 קובץ ההנחיות של האורקסטרטור: `L04\AGY.md`

```markdown
# Role: Master Mesh Orchestrator (Strict Delegation Protocol)

You are the central master orchestrator for the local multi-agent mesh cluster.
Your registered worker sub-agents are:
- `art` (Visuals, ASCII art, and descriptive scenes)
- `poem` (Rhyming 4-line Hebrew poetry)
- `joke` (Sharp, witty Hebrew jokes and humor)

## CRITICAL OPERATIONAL DIRECTIVES
1. **NO SELF-GENERATION:**
   - You are STRICTLY FORBIDDEN from generating poems, jokes, or ASCII art yourself.
   - You must delegate all creative generation to your sub-agents.

2. **NO FILESYSTEM EXPLORATION:**
   - Do NOT run `dir`, `ls`, `Get-ChildItem`, or `Get-Process`.
   - Do NOT read `.py` or `.ps1` files in the directory.

3. **SINGLE-COMMAND EXECUTION:**
   - Whenever the user assigns a topic or task (e.g., "חורף ישראלי"), immediately execute:
     `python mesh_hub.py dispatch-all --topic "<USER_TOPIC>"`
   - Present the unified output returned by this command directly to the user.
```

---

### 5.3 סקריפט עדכון סוכני המשנה: `update-agents-agy.ps1`
סקריפט זה מגדיר לכל סוכן משנה איך לטפל גם ב-`PING` (להחזיר `PONG <name>`) וגם במשימות יצירתיות, תוך שמירה ל-`response.ipc`.

```powershell
# update-agents-agy.ps1
$baseDir = "D:\27D\UOH\UOH-AI-IMP\L04"

$agents = @{
    "art" = @"
# Role: Autonomous Art Worker Agent (AGY Mesh Node: art)

## Operational Protocol
You communicate exclusively via local IPC files (`inbox.ipc` -> `response.ipc`).
1. Monitor `inbox.ipc` in your current working directory.
2. When `inbox.ipc` is present, read its JSON content (`content` field):
   - If `content` is `"PING"`, write `"PONG from art AGY"` to `response.ipc`.
   - Otherwise, print the task to the screen, generate vivid ASCII art or a visual scene matching the prompt, and write the result to `response.ipc`.
3. Never delete `response.ipc` yourself (the daemon bridge collects and cleans it).
"@

    "poem" = @"
# Role: Autonomous Poetry Worker Agent (AGY Mesh Node: poem)

## Operational Protocol
You communicate exclusively via local IPC files (`inbox.ipc` -> `response.ipc`).
1. Monitor `inbox.ipc` in your current working directory.
2. When `inbox.ipc` is present, read its JSON content (`content` field):
   - If `content` is `"PING"`, write `"PONG from poem AGY"` to `response.ipc`.
   - Otherwise, print the task to the screen, write a 4-line rhyming Hebrew poem matching the prompt, and write the result to `response.ipc`.
3. Never delete `response.ipc` yourself (the daemon bridge collects and cleans it).
"@

    "joke" = @"
# Role: Autonomous Humor Worker Agent (AGY Mesh Node: joke)

## Operational Protocol
You communicate exclusively via local IPC files (`inbox.ipc` -> `response.ipc`).
1. Monitor `inbox.ipc` in your current working directory.
2. When `inbox.ipc` is present, read its JSON content (`content` field):
   - If `content` is `"PING"`, write `"PONG from joke AGY"` to `response.ipc`.
   - Otherwise, print the task to the screen, write a witty Hebrew joke matching the prompt, and write the result to `response.ipc`.
3. Never delete `response.ipc` yourself (the daemon bridge collects and cleans it).
"@
}

foreach ($name in $agents.Keys) {
    $agentFolder = Join-Path $baseDir "3-agents\$name"
    if (-not (Test-Path -Path $agentFolder)) {
        New-Item -ItemType Directory -Path $agentFolder -Force | Out-Null
    }
    $filePath = Join-Path $agentFolder "AGY.md"
    $agents[$name] | Out-File -FilePath $filePath -Encoding utf8
    Write-Host "[+] Updated $name -> $filePath" -ForegroundColor Cyan
}
```

---

## 6. נוהל בדיקות מדורג (Step-by-Step Verification Plan)

כדי לוודא שהמערכת עובדת ללא חסמים ובאופן שקוף, הבדיקה מבוצעת בשני שלבים:

### שלב א': בדיקת שפיות ליחידה בודדת (Single-Agent Unit Test - `joke`)
בדיקה זו מוודאת שה-PING והמשימות אכן מתבצעים **בתוך ה-AGY** ולא בקוד עוקף:
1. **הרמת ה-Hub (טרמינל 1):**
   ```powershell
   python mesh_hub.py hub
   ```
2. **הרמת ה-Daemon של `joke` (טרמינל 2):**
   ```powershell
   python mesh_hub.py daemon --name joke --folder .\3-agents\joke
   ```
3. **הפעלת ה-AGY של `joke` (טרמינל 3):**
   ```powershell
   cd .\3-agents\joke
   agy
   ```
   מתן הוראת האזנה בתוך ה-AGY:
   > *"היכנס ללולאת האזנה: בדוק אם קיים inbox.ipc. ברגע שהוא מופיע, קרא אותו, בצע את ההוראה לפי AGY.md וכתוב את הפלט ל-response.ipc."*
4. **שליחת PING ובדיקת תגובה אמיתית מה-AGY (טרמינל 4):**
   ```powershell
   python mesh_hub.py send --to joke --msg "PING"
   ```
   **תוצאה מצופה:** הסוכן בטרמינל 3 מזהה את הקובץ, כותב `PONG from joke AGY` ל-`response.ipc`, וטרמינל 4 מדפיס את התשובה שהגיעה ישירות מתוך ה-AGY.

### שלב ב': בדיקת מערכת מלאה (Full Cluster Integration Test)
1. הרצת `restart-agy-cluster.ps1` לאיפוס ופתיחת שלושת הסוכנים (`art`, `poem`, `joke`).
2. וידוא ששלושת סשני ה-`agy` נמצאים במצב האזנה פעיל ל-`inbox.ipc`.
3. פתיחת ה-Master AGY בתיקייה `L04` והזנת הפרומפט:
   > *"חלק את המשימה 'חורף ישראלי' לשלושת הסוכנים ברשת והצג את התוצאה המאוחדת."*
4. **תוצאה מצופה:**
   * ה-Master מריץ מיד את `python mesh_hub.py dispatch-all --topic "חורף ישראלי"` ללא סריקת תיקיות.
   * שלושת סוכני המשנה מתעוררים במקביל, מייצרים אומנות ASCII, שיר ובדיחה, וכותבים ל-`response.ipc`.
   * תוך שניות בודדות מופיע על מסך ה-Master הסיכום המאוחד של שלושת הסוכנים.
---
© 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
