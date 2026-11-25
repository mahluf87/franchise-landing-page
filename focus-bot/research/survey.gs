/**
 * בונה את סקר "הזמן שלנו ברשתות" ב-Google Forms, עם גיליון תשובות מחובר.
 * הרצה: script.google.com ← פרויקט חדש ← להדביק את כל הקובץ ← Run (buildSurvey) ← לאשר הרשאות.
 * בסוף: View ← Logs (או Execution log) מציג קישור לטופס להפצה וקישור לגיליון התשובות.
 */
function buildSurvey() {
  var form = FormApp.create('הזמן שלנו ברשתות - סקר קצר');
  form.setDescription(
    'סקר של 3-4 דקות על הטלפון, הרשתות החברתיות והזמן שלנו.\n' +
    'הסקר אנונימי. בסוף אפשר (לא חובה) להשאיר פרטים אם תרצו להיות מהראשונים לנסות פתרון שאנחנו מפתחים.\n' +
    'תודה שאתם עוזרים!'
  );
  form.setProgressBar(true);
  form.setConfirmationMessage('תודה רבה! התשובות שלך יעזרו לנו לבנות משהו שבאמת עובד.');

  // ---------- עמוד 1: פרטים כלליים ----------
  form.addMultipleChoiceItem().setTitle('גיל').setRequired(true)
    .setChoiceValues(['18-24', '25-34', '35-44', '45-54', '55+']);
  form.addMultipleChoiceItem().setTitle('מגדר').setRequired(false)
    .setChoiceValues(['גבר', 'אישה', 'מעדיף/ה לא לענות']);
  form.addMultipleChoiceItem().setTitle('איזה טלפון יש לך?').setRequired(true)
    .setChoiceValues(['אנדרואיד (סמסונג, שיאומי, פיקסל וכו\')', 'אייפון', 'אחר']);
  var segment = form.addMultipleChoiceItem()
    .setTitle('מה מתאר אותך הכי טוב?')
    .setHelpText('אם כמה מתאימים, בחר/י את המרכזי. בהמשך תוכל/י לסמן עוד.')
    .setRequired(true);

  // ---------- עמוד: עצמאים ----------
  var pBiz = form.addPageBreakItem().setTitle('עסק ועבודה');
  form.addMultipleChoiceItem().setTitle('כמה מהזמן שלך ברשתות הוא לצורכי העסק (פרסום, לקוחות, תוכן)?').setRequired(true)
    .setChoiceValues(['כמעט הכול', 'רובו', 'בערך חצי', 'מיעוטו', 'כמעט כלום']);
  form.addCheckboxItem().setTitle('מה קורה לך? (אפשר לסמן כמה)').setRequired(false)
    .setChoiceValues([
      'נכנס/ת לפרסם או לענות ללקוח ונתקע/ת בפיד',
      'בודק/ת הודעות ורשתות כל כמה דקות',
      'קשה לי להתרכז במשימה ארוכה',
      'עובד/ת עד מאוחר כי היום "הלך" על הטלפון',
      'אף אחד מאלה'
    ]).showOtherOption(true);
  form.addMultipleChoiceItem().setTitle('כמה שעות עבודה בשבוע, לדעתך, הולכות על הסחות בטלפון?').setRequired(true)
    .setChoiceValues(['0-2', '3-5', '6-10', 'יותר מ-10', 'לא יודע/ת']);

  // ---------- עמוד: התפתחות אישית ----------
  var pDev = form.addPageBreakItem().setTitle('התפתחות אישית');
  form.addCheckboxItem().setTitle('איך את/ה עובד/ת על עצמך? (אפשר לסמן כמה)').setRequired(false)
    .setChoiceValues(['אימון אישי / קואצ\'ינג', 'קורסים או סדנאות', 'ספרים או פודקאסטים', 'מדיטציה / מיינדפולנס', 'אפליקציות הרגלים', 'טיפול'])
    .showOtherOption(true);
  form.addMultipleChoiceItem().setTitle('האם צמצום הזמן בטלפון וברשתות הוא חלק מהמטרות שלך?').setRequired(true)
    .setChoiceValues(['כן, וכבר עובד/ת על זה', 'כן, אבל עוד לא התחלתי', 'לא כרגע']);
  form.addMultipleChoiceItem().setTitle('אם היה לך מאמן/ת, היית מסכים/ה שיראה את הזמן שלך ברשתות כדי לעזור לך?').setRequired(true)
    .setChoiceValues(['כן', 'אולי', 'לא']);

  // ---------- עמוד: ספורט וכושר ----------
  var pFit = form.addPageBreakItem().setTitle('ספורט וכושר');
  form.addMultipleChoiceItem().setTitle('כמה פעמים בשבוע את/ה מתאמן/ת?').setRequired(true)
    .setChoiceValues(['1-2', '3-4', '5-6', 'כל יום']);
  form.addMultipleChoiceItem().setTitle('את/ה בטלפון בשעה שלפני השינה?').setRequired(true)
    .setChoiceValues(['כמעט כל ערב', 'לפעמים', 'כמעט אף פעם']);
  form.addMultipleChoiceItem().setTitle('את/ה מודד/ת שינה או התאוששות?').setRequired(true)
    .setChoiceValues(['כן, עם שעון חכם', 'כן, עם אפליקציה', 'לא']);
  form.addScaleItem().setTitle('כמה מעניין אותך לראות את הקשר בין הטלפון בערב לבין השינה והביצועים שלך?')
    .setBounds(1, 5).setLabels('לא מעניין', 'מאוד מעניין').setRequired(true);

  // ---------- עמוד משותף לכולם ----------
  var pAll = form.addPageBreakItem().setTitle('הזמן שלך ברשתות');
  form.addCheckboxItem().setTitle('מה עוד מתאים לך? (אפשר לסמן כמה)').setRequired(false)
    .setChoiceValues(['עצמאי/ת או בעל/ת עסק', 'בתהליך התפתחות אישית', 'מתאמן/ת באופן קבוע', 'הורה']);
  form.addMultipleChoiceItem().setTitle('כמה זמן ביום, לדעתך, את/ה ברשתות החברתיות?').setRequired(true)
    .setChoiceValues(['פחות משעה', '1-2 שעות', '2-3 שעות', '3-4 שעות', 'יותר מ-4 שעות']);
  form.addTextItem().setTitle('ואם בא לך לבדוק: כמה זה בפועל?')
    .setHelpText('בהגדרות הטלפון: "רווחה דיגיטלית" (אנדרואיד) או "זמן מסך" (אייפון). הממוצע היומי, לדוגמה: 2 שעות 40 דקות. לא חובה.')
    .setRequired(false);
  form.addScaleItem().setTitle('כמה את/ה רוצה לצמצם את הזמן ברשתות?')
    .setBounds(1, 10).setLabels('בכלל לא', 'מאוד').setRequired(true);
  form.addCheckboxItem().setTitle('מה הכי מטריד אותך בזמן ברשתות? (אפשר לסמן כמה)').setRequired(true)
    .setChoiceValues([
      'זמן שהולך לאיבוד',
      'פגיעה בריכוז ובפרודוקטיביות',
      'פגיעה בשינה',
      'מצב רוח, השוואה לאחרים',
      'פחות זמן עם משפחה וחברים',
      'שום דבר לא מטריד אותי'
    ]).showOtherOption(true);
  form.addCheckboxItem().setTitle('מה כבר ניסית? (אפשר לסמן כמה)').setRequired(true)
    .setChoiceValues([
      'הגבלה מובנית בטלפון (זמן מסך / רווחה דיגיטלית)',
      'אפליקציה ייעודית (Opal, one sec, מוח וכו\')',
      'מחיקת אפליקציות',
      'טלפון פשוט / "טלפון כשר"',
      'פשוט כוח רצון',
      'עוד לא ניסיתי כלום'
    ]).showOtherOption(true);
  form.addParagraphTextItem().setTitle('אם ניסית משהו, מה קרה? למה זה עבד או לא עבד?').setRequired(false);
  form.addCheckboxItem().setTitle('מה הכי היה עוזר לך? (עד 3)')
    .setRequired(true)
    .setValidation(FormApp.createCheckboxValidation().requireSelectAtMost(3).build())
    .setChoiceValues([
      'חסימה של האפליקציות כשהמכסה היומית נגמרת',
      'עצירה של כמה שניות לפני שאפליקציה נפתחת',
      'חבר או קבוצה שרואים את המספרים שלי',
      'מאמן (אדם או AI) שמדבר איתי על זה',
      'דוח שבועי שמראה לי את ההתקדמות',
      'תגמול כשאני עומד/ת ביעד',
      'הבנה של מה זה עושה לשינה, לריכוז ולמצב הרוח'
    ]);
  form.addMultipleChoiceItem().setTitle('כמה היית מוכן/ה לשלם בחודש על אפליקציה שבאמת מורידה לך את הזמן ברשתות בחצי?').setRequired(true)
    .setChoiceValues(['לא הייתי משלם/ת', 'עד 15 ₪', '15-30 ₪', '30-50 ₪', 'יותר מ-50 ₪']);
  form.addTextItem().setTitle('רוצה להיות מהראשונים לנסות? השאר/י מייל או טלפון')
    .setHelpText('לא חובה. נשתמש בזה רק כדי להזמין אותך לגרסת הניסיון, ולא נעביר לאף אחד.')
    .setRequired(false);

  // ---------- ניווט לפי "מה מתאר אותך" ----------
  segment.setChoices([
    segment.createChoice('עצמאי/ת או בעל/ת עסק', pBiz),
    segment.createChoice('בתהליך התפתחות אישית (אימון, קורסים, סדנאות)', pDev),
    segment.createChoice('מתאמן/ת באופן קבוע', pFit),
    segment.createChoice('אף אחד מאלה', pAll)
  ]);
  // בסוף כל עמוד ייעודי קופצים לעמוד המשותף (setGoToPage על מעבר העמוד שאחריו)
  pDev.setGoToPage(pAll); // אחרי עמוד "עסק"
  pFit.setGoToPage(pAll); // אחרי עמוד "התפתחות"
  // אחרי עמוד "כושר" ממשיכים לעמוד המשותף ממילא

  // ---------- גיליון תשובות ----------
  var ss = SpreadsheetApp.create('תשובות - הזמן שלנו ברשתות');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // טפסים חדשים עשויים להיווצר במצב "לא פורסם"; מפרסמים ופותחים לתשובות
  try { if (typeof form.setPublished === 'function') form.setPublished(true); } catch (e) {}
  form.setAcceptingResponses(true);

  Logger.log('קישור להפצה: ' + form.getPublishedUrl());
  Logger.log('עריכת הטופס: ' + form.getEditUrl());
  Logger.log('גיליון התשובות: ' + ss.getUrl());
}
