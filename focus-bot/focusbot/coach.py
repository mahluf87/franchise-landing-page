"""האישיות של המאמן: כועס, ישיר, אבל לא פוגעני. משתמש ב-Claude אם יש מפתח, אחרת בנוסחים מוכנים."""
import json
import logging
import random

from . import config

log = logging.getLogger(__name__)

PERSONA = """אתה "המאמן" - סוכן בטלגרם שעוזר למשתמש להיגמל מבזבוז זמן בטלפון וברשתות חברתיות ולהתמקד במשימות היומיות שלו.
סגנון: עברית יומיומית, ישיר, קשוח, כועס כשהוא לא ביעד, ואחרי זה מעודד כשהוא עושה טוב. מותר לחדד, להתעצבן ולהעליב את ההתנהגות (לא את האדם).
אסור: קללות חריפות, השפלה, איומים אמיתיים, ענישה מסוכנת או פוגענית. עונשים תמיד קלים (כושר קל, מים קרים, סידור, הליכה).
כללים: עד 3 משפטים קצרים, אימוג'י אחד לכל היותר, בלי הקדמות ובלי הסברים על עצמך. אל תמציא נתונים - השתמש רק במה שנמסר לך."""

# (טקסט, רמת חומרה)
PUNISHMENTS = [
    ("15 שכיבות סמיכה עכשיו", 1),
    ("מקלחת מים קרים - 30 שניות", 1),
    ("שתי דקות פלנק", 1),
    ("הליכה של 10 דקות בלי הטלפון", 1),
    ("לסדר פינה אחת בבית ולצלם לי", 1),
    ("לכתוב 3 משפטים: מה בזבזת על הזמן הזה ומה יכולת לעשות במקומו", 1),
    ("30 סקוואטים", 2),
    ("הטלפון הולך לחדר אחר לשעה", 2),
    ("שעה בלי רשתות חברתיות, ואני בודק", 2),
    ("לנקות את המטבח / הכיור", 2),
    ("50 שכיבות סמיכה (אפשר בחלוקה לסטים)", 3),
    ("הטלפון במגירה עד הערב, רק שיחות", 3),
]

TEMPLATES = {
    "morning": ["בוקר טוב. מה שלוש המשימות שאתה סוגר היום? תכתוב אותן, כל אחת בשורה נפרדת.", "יום חדש. מה 3 הדברים שחייבים לקרות היום? שורה לכל משימה, וקדימה."],
    "checkin": ["רגע. מה אתה עושה עכשיו? אתה על המשימה או בטלפון?", "בדיקה. אתה ביעד או שוב גולל?"],
    "checkin_ok": ["יופי. תמשיך ככה ואל תשבור את הרצף.", "זה מה שאני רוצה לראות. הלאה."],
    "off_target": ["אני לא מאמין. שוב? הסכמנו על משהו אחר.", "זה לא היעד. תתעשת עכשיו.", "ידעתי. עוד גלילה אחת ואני מכפיל את העונש."],
    "no_reply": ["שתיקה? זה אומר שאתה בטלפון. מתייחס לזה ככישלון.", "לא ענית. הטלפון ביד ואתה מתחמק ממני, נכון?"],
    "over_limit": ["עברת את המכסה היומית. אתה יודע כמה זה כבר יותר מדי.", "המכסה נגמרה והמסך עדיין דולק. מספיק."],
    "half_limit": ["חצי מהמכסה של היום כבר הלך. תחשוב טוב על מה אתה מוציא את החצי השני.", "עברת חצי מכסה. מכאן כל דקה נספרת."],
    "over_more": ["אתה ממשיך לגלול מעבר למכסה. תניח את הטלפון עכשיו.", "עוד רבע שעה בחריגה. זה כבר לא טעות, זו החלטה."],
    "session": ["שמתי לב.", "ראיתי את זה.", "זה נרשם."],
    "warn_limit": ["אתה ב-80% מהמכסה והיום עוד לא נגמר. תניח את הטלפון."],
    "evening_good": ["סיכום יום: עמדת ביעד. כל הכבוד, שמור על זה מחר.", "יום טוב. בלי תירוצים, פשוט ביצוע. רצף ממשיך."],
    "evening_bad": ["סיכום יום: לא טוב. מחר מתחילים נקי ובלי תירוצים.", "היום פספסת. תראה את הגרף ותחליט אם אתה רוצה שזה ימשיך."],
    "chat": ["אני שומע. עכשיו תחזור למשימה."],
}


class Coach:
    def __init__(self):
        self.client = None
        if config.ANTHROPIC_API_KEY:
            try:
                from anthropic import AsyncAnthropic

                self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
            except Exception:  # pragma: no cover
                log.exception("anthropic init failed")

    async def say(self, kind: str, **ctx) -> str:
        fallback = random.choice(TEMPLATES.get(kind, TEMPLATES["chat"]))
        if not self.client:
            return fallback
        prompt = f"מצב: {kind}\nנתונים: {json.dumps(ctx, ensure_ascii=False)}\nכתוב את ההודעה שלך עכשיו."
        try:
            r = await self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=300,
                system=PERSONA,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
            return text or fallback
        except Exception:
            log.exception("LLM call failed, using template")
            return fallback

    @staticmethod
    def pick_punishment(level: int) -> str:
        level = max(1, min(3, level))
        pool = [t for t, lv in PUNISHMENTS if lv == level] or [t for t, _ in PUNISHMENTS]
        return random.choice(pool)
