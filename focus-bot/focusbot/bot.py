import asyncio
import logging
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

HELP = """אני שומר לך על הזמן ברשתות החברתיות.
אני רואה כמה זמן אתה ברשתות, מעדכן אותך במהלך היום, כועס כשאתה מגזים ומעניש (קל) כשאתה חורג.

/usage - כמה זמן הייתי ברשתות היום
/report [ימים] - גרף
/limit 45 - מכסה יומית ברשתות, בדקות
/manual 40 - הזנה ידנית של דקות ברשתות היום
/punish - עונשים פתוחים
/pause 4 - להשהות עונשים ל-4 ימים
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


def social_limit():
    return db.limits()[1]


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


def fmt_long(m):
    """דקות בניסוח מלא: 'דקה', '22 דקות', 'שעה ו-12 דקות'."""
    m = int(round(m or 0))
    if m < 60:
        return "דקה" if m == 1 else f"{m} דקות"
    h, r = divmod(m, 60)
    hours = "שעה" if h == 1 else "שעתיים" if h == 2 else f"{h} שעות"
    return hours if r == 0 else f"{hours} ו-{'דקה' if r == 1 else f'{r} דקות'}"


def social_line(u, when="היום"):
    limit = social_limit()
    if not u:
        return f"📲 אין לי נתונים מהטלפון על {when}."
    used, left = u["social_min"], limit - u["social_min"]
    if int(round(used)) == 0:
        return f"📲 {when} עוד לא השתמשת ברשתות. המכסה שלך: {fmt_long(limit)}."
    head = f"📲 {when} השתמשת ברשתות {fmt_long(used)} מתוך מכסה של {fmt_long(limit)}."
    if when != "היום":
        return head
    if left >= 0.5:
        return head + f" נשארו לך {fmt_long(left)}."
    if left > -0.5:
        return head + " המכסה נגמרה."
    return head + f" חרגת ב-{fmt_long(-left)}."


def apps_breakdown(u):
    top = [(k, v) for k, v in sorted(u["apps"].items(), key=lambda kv: -kv[1]) if v >= 0.5 and db.is_social(k)][:6]
    return "\n".join(f"  • {k}: {fmt_long(v)}" for k, v in top)


def usage_text(u):
    out = [social_line(u)]
    if u:
        b = apps_breakdown(u)
        if b:
            out.append(b)
    return "\n".join(out)


def over_by(u):
    return max(u["social_min"] - social_limit(), 0) if u else 0


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def day_fraction(now=None):
    """כמה מ'היום הפעיל' עבר (0..1), לחישוב קצב."""
    now = now or datetime.now(config.TZ)
    start, end = _minutes(config.STATUS_DAY_START), _minutes(config.STATUS_DAY_END)
    cur = now.hour * 60 + now.minute
    return min(max((cur - start) / max(end - start, 1), 0), 1)


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
async def usage_cmd(update, ctx):
    await update.message.reply_text(usage_text(db.get_usage(db.today())))


@owner_only
async def manual(update, ctx):
    try:
        social = float(ctx.args[-1])
    except (IndexError, ValueError):
        return await update.message.reply_text("שימוש: /manual 40  (כמה דקות היית ברשתות היום)")
    db.set_usage(db.today(), social_min=social)
    await update.message.reply_text("נשמר.\n" + social_line(db.get_usage(db.today())))
    await handle_usage(ctx.application, db.today())


@owner_only
async def report(update, ctx):
    days = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 14
    days = max(3, min(days, 90))
    png = await asyncio.to_thread(charts.build_report, days)
    await update.message.reply_photo(png, caption=social_line(db.get_usage(db.today())))


@owner_only
async def limit_cmd(update, ctx):
    try:
        social = int(ctx.args[-1])  # /limit 45  (תואם גם לצורה הישנה /limit 120 45)
        if social <= 0:
            raise ValueError
    except (IndexError, ValueError):
        return await update.message.reply_text(f"המכסה היומית שלך ברשתות: {fmt_long(social_limit())}.\nלשינוי: /limit 45")
    db.set_setting("social_limit", social)
    await update.message.reply_text(f"עודכן. המכסה היומית ברשתות: {fmt_long(social)}.")


@owner_only
async def punish_cmd(update, ctx):
    ps = db.open_punishments()
    if not ps:
        return await update.message.reply_text("אין עונשים פתוחים.")
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
        f"עונשים מושהים. הם חוזרים ב-{until:%d/%m}.\n{n} עונשים פתוחים בוטלו.\nאני ממשיך למדוד ולעדכן אותך כרגיל."
    )


@owner_only
async def resume_cmd(update, ctx):
    db.set_setting("punish_paused_until", "")
    await update.message.reply_text("העונשים חזרו. מעכשיו כל חריגה עולה לך.")


async def on_button(update: Update, ctx):
    q = update.callback_query
    if owner_id() is not None and q.message.chat_id != owner_id():
        return await q.answer()
    kind, *rest = q.data.split(":")
    if kind == "pun":
        db.complete_punishment(int(rest[0]))
        await q.edit_message_reply_markup(None)
        await q.answer("מקובל.")
    else:  # כפתורים ישנים (משימות / בדיקות) שכבר לא קיימים
        await q.edit_message_reply_markup(None)
        await q.answer()


@owner_only
async def text_msg(update: Update, ctx):
    u = db.get_usage(db.today())
    reply = await coach.say("chat", user_message=(update.message.text or "").strip(),
                            social_today=round(u["social_min"]) if u else None, social_limit=social_limit())
    await update.message.reply_text(reply)


# ---------- usage alerts (נקרא כשהטלפון מדווח) ----------
async def handle_usage(app, day, event=None):
    """event = ('snapshot', תוספת דקות) מ-Tasker, או (שם אפליקציה, דקות) מ-MacroDroid."""
    if day != db.today():
        return
    u = db.get_usage(day)
    if not u:
        return
    limit = social_limit()
    used, over = u["social_min"], over_by(u)
    line = social_line(u)
    sent = False
    if over > 0:
        if db.flag_once(f"over_{day}"):
            await tell(app, await coach.say("over_limit", social=used, social_limit=limit) + "\n" + line)
            await issue_punishment(app, "חריגה מהמכסה", 1 if over < 30 else 2)
            sent = True
        else:
            step = int(over // 15)  # תזכורת על כל רבע שעה נוספת של חריגה
            if step >= 1 and db.flag_once(f"over_{day}_{step}"):
                await tell(app, await coach.say("over_more", over_minutes=int(over)) + "\n" + line)
                sent = True
    elif used >= 0.8 * limit:
        if db.flag_once(f"warn_{day}"):
            await tell(app, await coach.say("warn_limit", social=used, social_limit=limit) + "\n" + line)
            sent = True
    elif used >= 0.5 * limit:
        if db.flag_once(f"half_{day}"):
            await tell(app, await coach.say("half_limit", social=used, social_limit=limit) + "\n" + line)
            sent = True
    # תגובה על כל גלישה משמעותית, כדי שהגלילה לא תעבור בשקט
    if not sent and event and event[1] >= config.SESSION_NOTIFY_MIN:
        where = "ברשתות מאז העדכון הקודם" if event[0] == "snapshot" else f"ב-{event[0]}"
        comment = await coach.say("session", minutes=event[1], social_today=used, social_limit=limit)
        await tell(app, f"👀 היית עכשיו {fmt_long(event[1])} {where}. {comment}\n{line}")


# ---------- scheduled jobs ----------
async def morning_job(ctx):
    streak = db.streak()
    yday = (datetime.now(config.TZ).date() - timedelta(days=1)).isoformat()
    yu = db.get_usage(yday)
    msg = await coach.say("morning", streak_days=streak)
    if yu:
        verdict = "עמדת במכסה ✅" if over_by(yu) == 0 else "חרגת מהמכסה ❌"
        msg += f"\n\n{social_line(yu, 'אתמול')}\n{verdict}"
    msg += f"\n\nהמכסה להיום: {fmt_long(social_limit())} ברשתות."
    if streak:
        msg += f"\n🔥 רצף: {'יום אחד' if streak == 1 else f'{streak} ימים'} בתוך המכסה."
    await tell(ctx.application, msg)


async def status_job(ctx):
    """עדכון ביניים: כמה זמן ברשתות עד עכשיו, ביחס לקצב שמתאים למכסה."""
    u = db.get_usage(db.today())
    if u and db.get_setting("snapshot_day") != db.today() and u["social_min"] == 0 and not u["apps"]:
        u = None
    if not u:
        return await tell(ctx.application, "📲 הטלפון לא דיווח לי היום. בדוק ש-Tasker / MacroDroid פועלים.")
    used, limit = u["social_min"], social_limit()
    expected = limit * day_fraction()
    if over_by(u) > 0:
        kind = "status_over"
    elif round(used) == 0:
        kind = "status_zero"
    else:
        kind = "status_bad" if used > expected + 5 else "status_ok"
    comment = await coach.say(kind, social=used, social_limit=limit, expected_by_now=round(expected))
    await tell(ctx.application, f"{social_line(u)}\n{comment}")


async def evening_job(ctx):
    app = ctx.application
    day = db.today()
    u = db.get_usage(day)
    if not u:
        await tell(app, "הטלפון לא דיווח היום, אז אין לי מספרים. אני מניח הכי גרוע.")
        await issue_punishment(app, "אין דיווח שימוש", 1)
    else:
        good = over_by(u) == 0
        verdict = await coach.say("evening_good" if good else "evening_bad", social=u["social_min"], social_limit=social_limit())
        text = f"סיכום היום:\n{usage_text(u)}\n\n{verdict}"
        open_p = db.open_punishments()
        if open_p:
            text += f"\n⚖️ עונשים שלא בוצעו: {len(open_p)}"
        await tell(app, text)
        if not good and db.flag_once(f"over_{day}"):
            await issue_punishment(app, "חריגה מהמכסה", 1 if over_by(u) < 30 else 2)
    png = await asyncio.to_thread(charts.build_report, 14)
    await app.bot.send_photo(chat_id=owner_id(), photo=png, caption="הזמן שלך ברשתות ב-14 הימים האחרונים")


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
    for name, fn in [("start", start), ("help", help_cmd), ("usage", usage_cmd), ("manual", manual), ("report", report),
                     ("limit", limit_cmd), ("punish", punish_cmd), ("pause", pause_cmd), ("resume", resume_cmd)]:
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))

    jq = app.job_queue
    jq.run_daily(morning_job, _t(config.MORNING_TIME), name="morning")
    for i, t in enumerate(config.CHECKIN_TIMES):
        jq.run_daily(status_job, _t(t), name=f"status_{i}")
    jq.run_daily(evening_job, _t(config.EVENING_TIME), name="evening")

    app.run_polling()


if __name__ == "__main__":
    main()
