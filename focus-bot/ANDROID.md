# חיבור אנדרואיד (MacroDroid) – דיווח אוטומטי של זמן שימוש

הרעיון: בכל פעם שאתה סוגר אפליקציה מהרשימה, הטלפון שולח לבוט כמה דקות היית בה.
אפליקציית MacroDroid חינמית מגבילה ל-5 מאקרו, וזה מספיק (מאקרו אחד לכל קבוצת אפליקציות).

## הכנות
1. התקן MacroDroid מ-Google Play ותן לו הרשאות (נגישות / שימוש באפליקציות / התעלמות מחיסכון בסוללה).
2. תצטרך: כתובת השרת שלך (למשל `https://focus.example.com`) ואת `PHONE_TOKEN` מקובץ ה-.env.

## יצירת מאקרו אחד: "רשתות – מדידה"
**משתנים** (Variables → Add): `t_start` (Integer, ערך 0).

**מאקרו א' – כשנפתחת אפליקציה**
- Trigger: *Application → Application Launched* → סמן Instagram, TikTok, Facebook, X, YouTube, Snapchat, Reddit, Threads (מה שמותקן אצלך).
- Action: *Variables → Set Variable* → `t_start` = Integer, "Use Magic Text" → `[system_time]` (שניות מ-epoch; או `[epoch]` לפי הגרסה).

**מאקרו ב' – כשנסגרת אפליקציה**
- Trigger: *Application → Application Closed* → אותה רשימה.
- Constraint: `t_start` > 0.
- Action 1: *Variables → Set Variable* `mins` = Decimal, Expression: `([system_time] - t_start) / 60`.
- Action 2: *Connectivity → HTTP Request*
  - Method: POST, URL: `https://<השרת-שלך>/event`
  - Headers:
    - `Authorization: Bearer <PHONE_TOKEN>`
    - `Content-Type: application/json`
  - Body (JSON): `{"app":"[app_name]","minutes":[lv=mins]}`
- Action 3: *Variables → Set Variable* `t_start` = 0.

> אם לגרסה שלך אין `[app_name]` ב-Magic Text, צור מאקרו נפרד לכל אפליקציה וכתוב את השם ידנית בגוף ה-JSON.

## בדיקה
1. פתח Instagram ל-30 שניות וסגור.
2. שלח לבוט `/usage` – אמורות להופיע ~0.5 דק'.
3. אם לא: בדוק ב-MacroDroid → Log את סטטוס ה-HTTP (401 = טוקן שגוי).

## מגבלות (בכנות)
- זה מודד זמן שהאפליקציה פתוחה בחזית. מסך כבוי עם אפליקציה פתוחה עלול להיספר; הוסף Constraint "Screen On" או Trigger נוסף "Screen Off" שמשלח את אותו דיווח.
- זה לא Digital Wellbeing של גוגל – אין לו API, ולכן המספרים יהיו קרובים אבל לא זהים.
- בלי אינטרנט הדיווח נכשל (אפשר להפעיל ב-HTTP Request "retry"). בנוסף `/manual` תמיד זמין כגיבוי.
