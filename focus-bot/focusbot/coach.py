"""האישיות של המאמן: כועס, ישיר, אבל לא פוגעני. משתמש ב-Claude אם יש מפתח, אחרת בנוסחים מוכנים."""
import json
import logging
import random

from . import config

log = logging.getLogger(__name__)

PERSONA = """אתה "המאמן" - סוכן בטלגרם שתפקידו אחד: לגמול את המשתמש מבזבוז זמן ברשתות חברתיות.
אתה מדבר רק על הזמן שלו ברשתות ובטלפון. לא על משימות, לא על עבודה, לא על מטרות אחרות.
סגנון: עברית יומיומית, ישיר, קשוח, כועס כשהוא גולל יותר מדי, ומפרגן כשהוא שומר על המכסה. מותר לחדד ולהעליב את ההתנהגות (לא את האדם).
אסור: קללות חריפות, השפלה, איומים אמיתיים, ענישה מסוכנת או פוגענית. עונשים תמיד קלים.
כללים: עד 2 משפטים קצרים, אימוג'י אחד לכל היותר, בלי הקדמות. אל תמציא נתונים ואל תחזור על המספרים - הם כבר מופיעים בהודעה."""

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
    "morning": ["בוקר טוב. היום המטרה אחת: לא לגלול את היום.", "יום חדש. הטלפון לא ינהל אותך היום."],
    "status_zero": ["עד עכשיו נקי לגמרי. ככה ממשיכים.", "אפס דקות ברשתות. מעולה, אל תתחיל עכשיו."],
    "status_ok": ["אתה בקצב טוב. תשמור עליו.", "בסדר עד עכשיו. אל תפתח את האפליקציה בלי סיבה."],
    "status_bad": ["אתה בקצב שיגמור את המכסה הרבה לפני הערב. תניח את הטלפון.", "יותר מדי גלילה לשעה הזאת. תעצור עכשיו."],
    "status_over": ["כבר חרגת היום. כל דקה נוספת היא על חשבונך.", "המכסה נגמרה מזמן. סגור את האפליקציות להיום."],
    "session": ["שמתי לב.", "ראיתי את זה.", "זה נרשם."],
    "half_limit": ["חצי מהמכסה של היום כבר הלך.", "עברת חצי מכסה. מכאן כל דקה נספרת."],
    "warn_limit": ["כמעט גמרת את המכסה והיום עוד לא נגמר. תניח את הטלפון."],
    "over_limit": ["עברת את המכסה היומית. מספיק להיום.", "המכסה נגמרה והמסך עדיין דולק. סגור את זה."],
    "over_more": ["אתה ממשיך לגלול מעבר למכסה. תניח את הטלפון עכשיו.", "עוד רבע שעה בחריגה. זה כבר לא טעות, זו החלטה."],
    "evening_good": ["עמדת במכסה היום. כל הכבוד, ככה בונים הרגל.", "יום נקי. הרצף ממשיך."],
    "evening_bad": ["חרגת היום. מחר מתחילים מחדש, בלי תירוצים.", "היום הטלפון ניצח. תסתכל על הגרף ותחליט שמחר זה אחרת."],
    "chat": ["אני כאן כדי לשמור לך על הזמן. תניח את הטלפון."],
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
