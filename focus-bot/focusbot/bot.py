import asyncio
import logging
import re
from datetime import date, datetime, timedelta
from datetime import time as dtime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters)

from . import charts, config, db, server
from .coach import Coach

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
# httpx רושם כל בקשה כולל הטוקן בכתובת - משתיקים כדי שהטוקן לא ידלוף ללוגים
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
log = logging.getLogger("focusbot")
coach = Coach()

HELP = """אני המאמן שלך. אני שואל, בודק, כועס ומעניש (קל).

/plan - להגדיר משימות להיום
/tasks - רשימת משימות וסימון ביצוע
/add טקסט - להוסיף משימה
/checkin - בדיקה מיידית "אתה ביעד?"
/usage - שימוש היום
/manual 95 40 - הזנה ידנית: סך דקות, דקות ברשתות (למשל מ-Screen Time)
/report [ימים] - גרף התקדמות
/limit 120 45 - מכסה יומית: סך הכל, רשתות
/punish - עונשים פתוחים
/pause 4 - להשהות עונשים ל-4 ימים (או /pause 2026-11-19)
/resume - להחזיר עונשים
/help - העזרה הזאת"""


# ---------- helpers ----------
def owner_id():
    v = db.get_setting("owner_chat_id")
    return int(v) if v else None


def owner_only(fn):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        oid = owner_id()
        chat = update.effective_chat.id if update.effective_chat else None
        if oid is not None and chat != oid:
            return
        return await fn(update, ctx)

    return wrapper


async def tell(app, text, **kw):
    oid = owner_id()
    if oid:
        await app.bot.send_message(chat_id=oid, text=text, **kw)


def punishments_paused() -> bool:
    until = db.get_setting("punish_paused_until")
    return bool(until) and db.today() < until


async def issue_punishment(app, reason: str, level: int):
    if punishments_paused():
        return
    text = coach.pick_punishment(level)
    pid = db.add_punishment(db.today(), text, reason)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ ביצעתי", callback_data=f"pun:{pid}")]])
    await tell(app, f"⚖️ עונש: {text}", reply_markup=kb)


def fmt_min(m):
    m = int(round(m or 0))
    return f"{m // 60}:{m % 60:02d} שעות" if m >= 60 else f"{m} דק'"


def fmt_long(m):
    """דקות בניסוח מלא: 'דקה', '22 דקות', 'שעה ו-12 דקות'."""
    m = int(round(m or 0))
    if m < 60:
        return "דקה" if m == 1 else f"{m} דקות"
    h, r = divmod(m, 60)
    hours = "שעה" if h == 1 else "שעתיים" if h == 2 else f"{h} שעות"
    return hours if r == 0 else f"{hours} ו-{'דקה' if r == 1 else f'{r} דקות'}"


def usage_line(u):
    total_limit, _ = db.limits()
    if not u:
        return "📲 הטלפון עוד לא דיווח היום, אז אין לי נתוני שימוש."
    out = [social_line(u)]
    if u["total_min"] - u["social_min"] >= 1:
        out.append(f"📱 בכל האפליקציות שנמדדות: {fmt_long(u['total_min'])} מתוך מכסה של {fmt_long(total_limit)}.")
    if u.get("pickups"):
        out.append(f"🔓 הרמות טלפון: {u['pickups']}")
    top = [(k, v) for k, v in sorted(u["apps"].items(), key=lambda kv: -kv[1]) if v >= 0.5][:5]
    if top:
        out.append("פירוט:")
        out += [f"  • {k}: {fmt_long(v)}" for k, v in top]
    return "\n".join(out)


def social_line(u):
    _, social_limit = db.limits()
    if not u:
        return "📲 הטלפון עוד לא דיווח היום."
    used, left = u["social_min"], social_limit - u["social_min"]
    head = f"📲 היום השתמשת ברשתות {fmt_long(used)} מתוך מכסה של {fmt_long(social_limit)}."
    if int(round(used)) == 0:
        return f"📲 היום עוד לא השתמשת ברשתות. המכסה שלך: {fmt_long(social_limit)}."
    if left >= 0.5:
        return head + f" נשארו לך {fmt_long(left)}."
    if left > -0.5:
        return head + " המכסה נגמרה."
    return head + f" חרגת ב-{fmt_long(-left)}."


def over_by(u):
    total_limit, social_limit = db.limits()
    return max(u["total_min"] - total_limit, u["social_min"] - social_limit, 0)


# ---------- commands ----------
async def start(update: Update, ctx):
    oid = owner_id()
    chat = update.effective_chat.id
    if oid is None:
        db.set_setting("owner_chat_id", chat)
        await update.message.reply_text("נרשמת כבעלים. מעכשיו אני על הגב שלך.\n\n" + HELP)
    elif oid == chat:
        await update.message.reply_text(HELP)


@owner_only
async def help_cmd(update, ctx):
    await update.message.reply_text(HELP)


@owner_only
async def plan(update, ctx):
    ctx.application.bot_data["awaiting"] = "plan"
    await update.message.reply_text(await coach.say("morning"))


@owner_only
async def add(update, ctx):
    text = " ".join(ctx.args).strip()
    if not text:
        return await update.message.reply_text("שימוש: /add כתיבת הצעת מחיר")
    db.add_task(db.today(), text)
    await update.message.reply_text(f"נוספה: {text}")


@owner_only
async def tasks_cmd(update, ctx):
    ts = db.tasks(db.today())
    if not ts:
        return await update.message.reply_text("אין משימות להיום. /plan")
    kb = [[InlineKeyboardButton(("✅ " if t["done"] else "⬜ ") + t["text"], callback_data=f"task:{t['id']}")] for t in ts]
    await update.message.reply_text("המשימות של היום (לחץ לסימון):", reply_markup=InlineKeyboardMarkup(kb))


@owner_only
async def usage_cmd(update, ctx):
    await update.message.reply_text(usage_line(db.get_usage(db.today())))


@owner_only
async def manual(update, ctx):
    try:
        total = float(ctx.args[0])
        social = float(ctx.args[1]) if len(ctx.args) > 1 else None
    except (IndexError, ValueError):
        return await update.message.reply_text("שימוש: /manual <סך דקות> [דקות ברשתות]")
    db.set_usage(db.today(), total_min=total, social_min=social)
    await update.message.reply_text("נשמר.\n" + usage_line(db.get_usage(db.today())))
    await handle_usage(ctx.application, db.today())


@owner_only
async def report(update, ctx):
    days = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 14
    days = max(3, min(days, 90))
    png = await asyncio.to_thread(charts.build_report, days)
    await update.message.reply_photo(png, caption=usage_line(db.get_usage(db.today())))


@owner_only
async def limit_cmd(update, ctx):
    try:
        total, social = int(ctx.args[0]), int(ctx.args[1])
    except (IndexError, ValueError):
        t, s = db.limits()
        return await update.message.reply_text(f"המכסה היומית שלך: {fmt_long(s)} ברשתות, {fmt_long(t)} בסך הכל.\nלשינוי: /limit 120 45 (קודם סך הכל, אחר כך רשתות)")
    db.set_setting("total_limit", total)
    db.set_setting("social_limit", social)
    await update.message.reply_text(f"עודכן. המכסה היומית: {fmt_long(social)} ברשתות, {fmt_long(total)} בסך הכל.")


@owner_only
async def punish_cmd(update, ctx):
    ps = db.open_punishments()
    if not ps:
        return await update.message.reply_text("אין עונשים פתוחים. תמשיך להתנהג יפה.")
    for p in ps:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ ביצעתי", callback_data=f"pun:{p['id']}")]])
        await update.message.reply_text(f"⚖️ {p['text']}\n(על: {p['reason']}, {p['day']})", reply_markup=kb)


@owner_only
async def pause_cmd(update, ctx):
    arg = ctx.args[0] if ctx.args else ""
    today = datetime.now(config.TZ).date()
    try:
        until = today + timedelta(days=int(arg)) if arg.isdigit() else date.fromisoformat(arg)
    except ValueError:
        cur = db.get_setting("punish_paused_until")
        state = f"מושהים עד {cur}" if punishments_paused() else "פעילים"
        return await update.message.reply_text(f"עונשים כרגע: {state}.\nשימוש: /pause 4 (ימים) או /pause 2026-11-19")
    if until <= today:
        return await update.message.reply_text("התאריך צריך להיות בעתיד.")
    db.set_setting("punish_paused_until", until.isoformat())
    n = db.clear_open_punishments()
    await update.message.reply_text(
        f"עונשים מושהים. הם חוזרים ב-{until:%d/%m}.\n{n} עונשים פתוחים בוטלו.\nאני ממשיך למדוד, לשאול ולכעוס כרגיל."
    )


@owner_only
async def resume_cmd(update, ctx):
    db.set_setting("punish_paused_until", "")
    await update.message.reply_text("העונשים חזרו. מעכשיו כל חריגה עולה לך.")


@owner_only
async def checkin_cmd(update, ctx):
    await send_checkin(ctx.application)


# ---------- check-in flow ----------
async def send_checkin(app):
    cid = db.new_checkin(db.today())
    pending = [t["text"] for t in db.tasks(db.today()) if not t["done"]]
    text = await coach.say("checkin", open_tasks=pending)
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ על המשימה", callback_data=f"ci:ok:{cid}"), InlineKeyboardButton("❌ סטיתי", callback_data=f"ci:off:{cid}")]]
    )
    text += "\n\n" + social_line(db.get_usage(db.today()))
    if pending:
        text += "\nפתוח: " + ", ".join(pending[:3])
    await tell(app, text, reply_markup=kb)
    app.job_queue.run_once(checkin_timeout, config.CHECKIN_TIMEOUT_MIN * 60, data=cid, name=f"ci_timeout_{cid}")


async def checkin_timeout(ctx: ContextTypes.DEFAULT_TYPE):
    cid = ctx.job.data
    if db.checkin_status(cid) != "pending":
        return
    db.set_checkin(cid, "missed")
    await tell(ctx.application, await coach.say("no_reply", minutes=config.CHECKIN_TIMEOUT_MIN))
    await issue_punishment(ctx.application, "לא ענה לבדיקה", 1)


async def on_button(update: Update, ctx):
    q = update.callback_query
    if owner_id() is not None and q.message.chat_id != owner_id():
        return await q.answer()
    kind, *rest = q.data.split(":")
    app = ctx.application
    if kind == "ci":
        action, cid = rest[0], int(rest[1])
        if db.checkin_status(cid) != "pending":
            return await q.answer("כבר ענית על זה")
        for j in app.job_queue.get_jobs_by_name(f"ci_timeout_{cid}"):
            j.schedule_removal()
        await q.edit_message_reply_markup(None)
        if action == "ok":
            db.set_checkin(cid, "ok")
            await q.answer()
            await tell(app, await coach.say("checkin_ok"))
        else:
            db.set_checkin(cid, "off")
            await q.answer()
            counts = db.checkin_counts(db.today())
            n_off = counts.get("off", 0) + counts.get("missed", 0)
            app.bot_data["awaiting"] = f"reason:{cid}"
            await tell(app, await coach.say("off_target", offs_today=n_off) + "\n\nמה גרם לזה? תכתוב לי במשפט אחד.")
            await issue_punishment(app, "סטייה מהיעד", 1 if n_off < 3 else 2)
    elif kind == "task":
        tid = int(rest[0])
        t = next((x for x in db.tasks(db.today()) if x["id"] == tid), None)
        if t:
            db.set_task_done(tid, 0 if t["done"] else 1)
        ts = db.tasks(db.today())
        kb = [[InlineKeyboardButton(("✅ " if x["done"] else "⬜ ") + x["text"], callback_data=f"task:{x['id']}")] for x in ts]
        await q.edit_message_reply_markup(InlineKeyboardMarkup(kb))
        await q.answer("עודכן")
    elif kind == "pun":
        db.complete_punishment(int(rest[0]))
        await q.edit_message_reply_markup(None)
        await q.answer("מקובל. עכשיו תחזור לעבוד.")


# ---------- free text ----------
@owner_only
async def text_msg(update: Update, ctx):
    text = (update.message.text or "").strip()
    awaiting = ctx.application.bot_data.get("awaiting")
    if awaiting == "plan":
        lines = [re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", ln).strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]
        for ln in lines:
            db.add_task(db.today(), ln)
        ctx.application.bot_data["awaiting"] = None
        return await update.message.reply_text(f"נרשמו {len(lines)} משימות. בערב אני בודק כמה סגרת. /tasks")
    if awaiting and awaiting.startswith("reason:"):
        db.set_checkin(int(awaiting.split(":")[1]), "off", note=text)
        ctx.application.bot_data["awaiting"] = None
        return await update.message.reply_text("רשמתי. עכשיו תקום ותחזור למשימה.")
    reply = await coach.say("chat", user_message=text, open_tasks=[t["text"] for t in db.tasks(db.today()) if not t["done"]])
    await update.message.reply_text(reply)


# ---------- usage alerts (נקרא כשהטלפון מדווח) ----------
async def handle_usage(app, day, event=None):
    """event = (שם אפליקציה, דקות) כשהדיווח הוא על שהייה בודדת."""
    if day != db.today():
        return
    u = db.get_usage(day)
    if not u:
        return
    total_limit, social_limit = db.limits()
    over = over_by(u)
    ratio = max(u["total_min"] / max(total_limit, 1), u["social_min"] / max(social_limit, 1))
    line = social_line(u)
    sent = False
    if over > 0:
        if db.flag_once(f"over_{day}"):
            await tell(app, await coach.say("over_limit", total=u["total_min"], social=u["social_min"], total_limit=total_limit, social_limit=social_limit) + "\n" + line)
            await issue_punishment(app, "חריגה מהמכסה", 1 if over < 30 else 2)
            sent = True
        else:
            step = int(over // 15)  # תזכורת נוספת על כל רבע שעה של חריגה
            if step >= 1 and db.flag_once(f"over_{day}_{step}"):
                await tell(app, await coach.say("over_more", over_minutes=int(over)) + "\n" + line)
                sent = True
    elif ratio >= 0.8:
        if db.flag_once(f"warn_{day}"):
            await tell(app, await coach.say("warn_limit", total=u["total_min"], social=u["social_min"]) + "\n" + line)
            sent = True
    elif ratio >= 0.5:
        if db.flag_once(f"half_{day}"):
            await tell(app, await coach.say("half_limit", social=u["social_min"], social_limit=social_limit) + "\n" + line)
            sent = True
    # תגובה מיידית על כל שהייה משמעותית, כדי שהגלילה לא תעבור בשקט
    if not sent and event and event[1] >= config.SESSION_NOTIFY_MIN:
        await tell(app, f"👀 היית עכשיו {fmt_long(event[1])} ב-{event[0]}. " + await coach.say("session", app=event[0], minutes=event[1], social_today=u["social_min"], social_limit=social_limit) + "\n" + line)


# ---------- scheduled jobs ----------
async def morning_job(ctx):
    ctx.application.bot_data["awaiting"] = "plan"
    streak = db.streak()
    msg = await coach.say("morning", streak_days=streak)
    yday = (datetime.now(config.TZ).date() - timedelta(days=1)).isoformat()
    yu = db.get_usage(yday)
    if yu:
        _, social_limit = db.limits()
        verdict = "עמדת במכסה" if over_by(yu) == 0 else "חרגת מהמכסה"
        msg += f"\n\nאתמול השתמשת ברשתות {fmt_long(yu['social_min'])} מתוך מכסה של {fmt_long(social_limit)} - {verdict}."
    await tell(ctx.application, msg + (f"\n🔥 רצף: {streak} ימים" if streak else ""))


async def checkin_job(ctx):
    await send_checkin(ctx.application)


async def evening_job(ctx):
    app = ctx.application
    day = db.today()
    u = db.get_usage(day)
    ts = db.tasks(day)
    done = sum(t["done"] for t in ts)
    summary = usage_line(u) + f"\n✅ משימות: {done}/{len(ts)}"
    open_p = db.open_punishments()
    if open_p:
        summary += f"\n⚖️ עונשים שלא בוצעו: {len(open_p)}"
    if not u:
        await tell(app, "הטלפון לא דיווח היום, אז אני מניח הכי גרוע.\n" + summary)
        await issue_punishment(app, "אין דיווח שימוש", 1)
    else:
        good = over_by(u) == 0 and (not ts or done >= len(ts) / 2)
        verdict = await coach.say("evening_good" if good else "evening_bad", usage=u, tasks_done=done, tasks_total=len(ts))
        await tell(app, verdict + "\n\n" + summary)
        if over_by(u) > 0 and db.flag_once(f"over_{day}"):
            await issue_punishment(app, "חריגה מהמכסה", 1 if over_by(u) < 30 else 2)
    png = await asyncio.to_thread(charts.build_report, 14)
    await app.bot.send_photo(chat_id=owner_id(), photo=png, caption="ההתקדמות שלך ב-14 הימים האחרונים")


def _t(s):
    h, m = s.split(":")
    return dtime(int(h), int(m), tzinfo=config.TZ)


def main():
    if not config.TOKEN:
        raise SystemExit("חסר TELEGRAM_BOT_TOKEN (ראה .env.example)")

    async def post_init(app: Application):
        loop = asyncio.get_running_loop()

        def on_update(day, event=None):
            asyncio.run_coroutine_threadsafe(handle_usage(app, day, event), loop)

        server.start(on_update)

    app = Application.builder().token(config.TOKEN).post_init(post_init).build()
    for name, fn in [("start", start), ("help", help_cmd), ("plan", plan), ("add", add), ("tasks", tasks_cmd), ("usage", usage_cmd),
                     ("manual", manual), ("report", report), ("limit", limit_cmd), ("punish", punish_cmd), ("pause", pause_cmd), ("resume", resume_cmd), ("checkin", checkin_cmd)]:
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))

    jq = app.job_queue
    jq.run_daily(morning_job, _t(config.MORNING_TIME), name="morning")
    for i, t in enumerate(config.CHECKIN_TIMES):
        jq.run_daily(checkin_job, _t(t), name=f"checkin_{i}")
    jq.run_daily(evening_job, _t(config.EVENING_TIME), name="evening")

    app.run_polling()


if __name__ == "__main__":
    main()
