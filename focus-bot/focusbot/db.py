"""שכבת נתונים (SQLite). כל פונקציה פותחת חיבור משלה כדי שתעבוד גם משרשור השרת."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS usage (
    day TEXT PRIMARY KEY, total_min REAL DEFAULT 0, social_min REAL DEFAULT 0,
    pickups INTEGER DEFAULT 0, apps TEXT DEFAULT '{}', updated_at TEXT);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, text TEXT, done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, ts TEXT, status TEXT DEFAULT 'pending', note TEXT);
CREATE TABLE IF NOT EXISTS punishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, text TEXT, reason TEXT, done INTEGER DEFAULT 0);
"""


@contextmanager
def conn():
    import os

    os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)
    c = sqlite3.connect(config.DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()


def today() -> str:
    return datetime.now(config.TZ).date().isoformat()


# ---- settings ----
def get_setting(key, default=None):
    with conn() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default


def set_setting(key, value):
    with conn() as c:
        c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))


def limits():
    return (
        int(get_setting("total_limit", config.DEFAULT_TOTAL_LIMIT)),
        int(get_setting("social_limit", config.DEFAULT_SOCIAL_LIMIT)),
    )


def flag_once(name: str) -> bool:
    """True אם זו הפעם הראשונה שהדגל הזה נקבע (למניעת התראות כפולות)."""
    if get_setting(name) is not None:
        return False
    set_setting(name, "1")
    return True


# ---- usage ----
def is_social(app_name: str) -> bool:
    n = app_name.lower().strip()
    # שמות קצרים (כמו "X") נבדקים בהתאמה מלאה, אחרת "x" היה תופס גם Netflix/Firefox
    return any(n == s or (len(s) > 2 and s in n) for s in config.SOCIAL_APPS)


def set_usage(day, total_min=None, social_min=None, pickups=None, apps=None, replace_apps=False):
    """דיווח מצטבר של היום (מחליף ערכים קיימים)."""
    apps = apps or {}
    if social_min is None and apps:
        social_min = sum(v for k, v in apps.items() if is_social(k))
    if total_min is None and apps:
        total_min = sum(apps.values())
    with conn() as c:
        old = c.execute("SELECT * FROM usage WHERE day=?", (day,)).fetchone()
        merged_apps = {} if replace_apps or not old else json.loads(old["apps"])
        merged_apps.update(apps)
        c.execute(
            "INSERT INTO usage(day,total_min,social_min,pickups,apps,updated_at) VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(day) DO UPDATE SET total_min=excluded.total_min, social_min=excluded.social_min, "
            "pickups=excluded.pickups, apps=excluded.apps, updated_at=excluded.updated_at",
            (
                day,
                total_min if total_min is not None else (old["total_min"] if old else 0),
                social_min if social_min is not None else (old["social_min"] if old else 0),
                pickups if pickups is not None else (old["pickups"] if old else 0),
                json.dumps(merged_apps, ensure_ascii=False),
                datetime.now(config.TZ).isoformat(timespec="seconds"),
            ),
        )


def add_app_time(day, app_name, minutes):
    """אירוע בודד: הוספת דקות לאפליקציה (למשל מ-MacroDroid / Tasker)."""
    u = get_usage(day)
    apps = dict(u["apps"]) if u else {}
    apps[app_name] = round(apps.get(app_name, 0) + minutes, 2)
    total = (u["total_min"] if u else 0) + minutes
    social = (u["social_min"] if u else 0) + (minutes if is_social(app_name) else 0)
    set_usage(day, total_min=total, social_min=social, apps=apps)


def get_usage(day):
    with conn() as c:
        r = c.execute("SELECT * FROM usage WHERE day=?", (day,)).fetchone()
    if not r:
        return None
    d = dict(r)
    d["apps"] = json.loads(d["apps"] or "{}")
    return d


def usage_range(days: int):
    start = (datetime.now(config.TZ).date() - timedelta(days=days - 1)).isoformat()
    with conn() as c:
        rows = c.execute("SELECT * FROM usage WHERE day>=? ORDER BY day", (start,)).fetchall()
    return {r["day"]: dict(r) for r in rows}


def save_snapshot(day, packages, seconds):
    """תמונת מצב מדויקת מאנדרואיד (Tasker App Info): זמן בחזית לכל חבילה מאז חצות.
    מחליפה את כל מה שנמדד היום ומחזירה את התוספת בדקות-רשתות מאז הדיווח הקודם."""
    before = get_usage(day)
    prev_social = before["social_min"] if before else 0
    apps, social, total = {}, 0.0, 0.0
    for pkg, sec in zip(packages, seconds):
        pkg = pkg.strip()
        try:
            m = max(float(sec), 0) / 60
        except ValueError:
            continue
        if not pkg or m <= 0:
            continue
        total += m
        if pkg in config.SOCIAL_PACKAGES:
            name = config.SOCIAL_PACKAGES[pkg]
            apps[name] = round(apps.get(name, 0) + m, 2)
            social += m
    set_usage(day, total_min=round(total, 2), social_min=round(social, 2), apps=apps, replace_apps=True)
    set_setting("snapshot_day", day)
    return max(social - prev_social, 0)


def streak() -> int:
    """ימים רצופים (עד אתמול) שבהם הזמן ברשתות היה בתוך המכסה."""
    _, social_limit = limits()
    n = 0
    d = datetime.now(config.TZ).date() - timedelta(days=1)
    while True:
        u = get_usage(d.isoformat())
        if not u or u["social_min"] > social_limit:
            break
        n += 1
        d -= timedelta(days=1)
    return n


# ---- tasks ----
def add_task(day, text):
    with conn() as c:
        c.execute("INSERT INTO tasks(day,text) VALUES(?,?)", (day, text))


def tasks(day):
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM tasks WHERE day=? ORDER BY id", (day,))]


def set_task_done(task_id, done=1):
    with conn() as c:
        c.execute("UPDATE tasks SET done=? WHERE id=?", (done, task_id))


def task_rate(days: int):
    start = (datetime.now(config.TZ).date() - timedelta(days=days - 1)).isoformat()
    with conn() as c:
        rows = c.execute("SELECT day, COUNT(*) n, SUM(done) d FROM tasks WHERE day>=? GROUP BY day", (start,)).fetchall()
    return {r["day"]: (100.0 * (r["d"] or 0) / r["n"]) for r in rows if r["n"]}


# ---- checkins ----
def new_checkin(day) -> int:
    with conn() as c:
        cur = c.execute("INSERT INTO checkins(day,ts) VALUES(?,?)", (day, datetime.now(config.TZ).isoformat(timespec="seconds")))
        return cur.lastrowid


def checkin_status(cid):
    with conn() as c:
        r = c.execute("SELECT status FROM checkins WHERE id=?", (cid,)).fetchone()
    return r["status"] if r else None


def set_checkin(cid, status, note=None):
    with conn() as c:
        c.execute("UPDATE checkins SET status=?, note=COALESCE(?,note) WHERE id=?", (status, note, cid))


def last_checkin(day):
    with conn() as c:
        r = c.execute("SELECT * FROM checkins WHERE day=? ORDER BY id DESC LIMIT 1", (day,)).fetchone()
    return dict(r) if r else None


def checkin_counts(day):
    with conn() as c:
        rows = c.execute("SELECT status, COUNT(*) n FROM checkins WHERE day=? GROUP BY status", (day,)).fetchall()
    return {r["status"]: r["n"] for r in rows}


# ---- punishments ----
def add_punishment(day, text, reason) -> int:
    with conn() as c:
        return c.execute("INSERT INTO punishments(day,text,reason) VALUES(?,?,?)", (day, text, reason)).lastrowid


def complete_punishment(pid):
    with conn() as c:
        c.execute("UPDATE punishments SET done=1 WHERE id=?", (pid,))


def open_punishments():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM punishments WHERE done=0 ORDER BY id")]


def clear_open_punishments() -> int:
    with conn() as c:
        return c.execute("UPDATE punishments SET done=1 WHERE done=0").rowcount


def punishments_today_count(day):
    with conn() as c:
        return c.execute("SELECT COUNT(*) n FROM punishments WHERE day=?", (day,)).fetchone()["n"]
