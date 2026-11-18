# Focus Bot — המאמן שלך בטלגרם

בוט טלגרם שעוזר להיגמל מבזבוז זמן ברשתות חברתיות. הוא מדבר רק על הזמן שלך ברשתות.

## מה הוא עושה
- **בוקר:** שואל מה המשימות להיום (`/plan`).
- **במשך היום:** 5 בדיקות ("אתה ביעד?") עם כפתורים. לחצת "סטיתי" או לא ענית תוך 20 דק' → כעס + עונש קל.
- **שימוש בטלפון:** הטלפון מדווח לבוט. ב-80% מהמכסה אזהרה, בחריגה כעס + עונש מיידי.
- **ערב:** סיכום, פסק דין, וגרף התקדמות (זמן מסך, רשתות, אחוז משימות, רצף ימים). גם לפי דרישה: `/report`.
- **עונשים:** קלים בלבד (שכיבות סמיכה, מים קרים, סידור, הליכה...). אתה מאשר ביצוע בכפתור, והבוט מזכיר עונשים פתוחים.
- אם מוגדר `ANTHROPIC_API_KEY`, ההודעות נכתבות ע"י Claude (כל פעם אחרת, לפי ההקשר). בלי מפתח - נוסחים מוכנים.

## הרצה
1. פתח בוט ב-[@BotFather](https://t.me/BotFather) וקבל טוקן.
2. `cp .env.example .env` ומלא `TELEGRAM_BOT_TOKEN` ו-`PHONE_TOKEN` (סיסמה אקראית ארוכה).
3. `pip install -r requirements.txt && python run.py`
4. שלח `/start` לבוט - הצ'אט שלך נרשם כבעלים והבוט מתעלם מכל אחד אחר.

**פריסה על VPS (מומלץ):** `DOMAIN=focus.example.com docker compose up -d --build` (Caddy מטפל ב-HTTPS).

הבוט חייב לרוץ 24/7 ולהיות נגיש מהאינטרנט (בשביל דיווחי הטלפון): VPS זול, Railway/Fly.io/Render, או Docker:
`docker build -t focusbot . && docker run -d --env-file .env -p 8080:8080 -v focus-data:/app/data focusbot`
(שים מאחורי HTTPS - Caddy / Cloudflare Tunnel / ה-proxy של הפלטפורמה.)

## חיבור הטלפון
טלגרם עצמו **לא** יכול לראות את זמן המסך שלך - הטלפון צריך לדווח. ה-API:

```
POST https://<הכתובת-שלך>/usage     Authorization: Bearer <PHONE_TOKEN>
{"total_minutes": 95, "social_minutes": 40, "pickups": 60, "apps": {"Instagram": 25, "TikTok": 15}}
```
מצטבר ליום הנוכחי (כל דיווח מחליף את הקודם). לחלופין, אירוע בודד שנוסף לסכום: `POST /event {"app":"Instagram","minutes":3.5}`.

### אנדרואיד – מדויק (מומלץ)
[TASKER.md](TASKER.md): קורא את המספרים של אנדרואיד עצמו ושולח כל 15 דקות.

### אנדרואיד – משוער
מדריך מלא צעד-צעד: [ANDROID.md](ANDROID.md).
**MacroDroid / Tasker**: טריגר "אפליקציה נסגרה" לרשימת האפליקציות → מחשבים משך מאז שנפתחה → פעולת HTTP POST ל-`/event` עם שם האפליקציה והדקות. ל-MacroDroid זה בונים בכמה דקות מהתבנית "Application Launched/Closed" + משתנה זמן.

### אייפון
אפל לא חושפת את Screen Time לשום אוטומציה. שתי דרכים: (1) כל ערב `/manual 95 40` (סך דקות, דקות ברשתות) מהמספרים ב-Screen Time. (2) קיצורי דרך → אוטומציה "כשפותחים Instagram/TikTok" → פעולת "Get contents of URL" (POST ל-`/event`) כדי לספור פתיחות - לא משך.

## פקודות
`/plan` `/tasks` `/add` `/checkin` `/usage` `/manual` `/report [ימים]` `/limit 120 45` `/punish` `/help`

## התאמות
שעות הבדיקות, המכסות, רשימת אפליקציות ה"רשתות" - ב-`.env`. העונשים והאישיות - ב-`focusbot/coach.py`.
