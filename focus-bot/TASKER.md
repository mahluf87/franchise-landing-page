# דיווח מדויק עם Tasker

MacroDroid מודד בעצמו פתיחה וסגירה של אפליקציות, ולכן הוא מפספס (מסך כבוי, מעבר בין אפליקציות).
Tasker קורא את המספרים של אנדרואיד עצמו (אותו מקור כמו "רווחה דיגיטלית") ושולח אותם לבוט כל 15 דקות.

## התקנה
1. Tasker מ-Google Play (תשלום חד-פעמי).
2. הגדרות הטלפון ← אפליקציות ← גישה מיוחדת ← **גישה לנתוני שימוש** ← Tasker ← לאפשר.
3. הגדרות ← אפליקציות ← Tasker ← סוללה ← **ללא הגבלה**.

## Task בשם `FocusReport` (שלוש פעולות)
1. **Variables ← Variable Set**
   - Name: `%since`
   - To: `floor(%TIME)*60 + round((%TIME - floor(%TIME))*100) + 1`
   - Do Maths: ✅
   (כמה דקות עברו מחצות)
2. **App ← App Info**
   - App: `most(time,%since:0,100)`
   (כל האפליקציות שהיו בשימוש מאז חצות; הזמן בשניות נשמר ב-`%app_used()` והחבילה ב-`%app_package()`)
3. **Net ← HTTP Request**
   - Method: `POST`
   - URL: `https://<השרת>/focus/snapshot`
   - Headers (שורה לכל כותרת):
     ```
     Authorization:Bearer <PHONE_TOKEN>
     Content-Type:application/json
     ```
   - Body:
     ```
     {"packages":"%app_package()","seconds":"%app_used()"}
     ```

## Profile
**Time** ← From `00:00` To `23:59`, Repeat `15` minutes ← משייכים ל-`FocusReport`.

## בדיקה
מריצים את ה-Task ידנית (▶). בבוט: `/usage` צריך להראות את אותם מספרים כמו "רווחה דיגיטלית".

## אחרי שזה עובד
לכבות את המאקרו `Focus` ב-MacroDroid. השרת ממילא מתעלם מדיווחי MacroDroid ביום שבו הגיע דיווח מ-Tasker.

## אפליקציות שנספרות
Instagram, Threads, Facebook, TikTok, YouTube, X, Snapchat, Reddit.
להוספה/הסרה: משתנה `SOCIAL_PACKAGES` בקובץ `.env` בשרת (`חבילה:שם`, מופרד בפסיקים).
