/**
 * בונה את הסקר "הטלפון והזמן שלנו" ב-Google Forms, עם גיליון תשובות מחובר.
 * הסקר אנונימי: לא נאספים מיילים, שמות או פרטי קשר.
 *
 * הרצה: script.google.com ← פרויקט חדש ← להדביק את כל הקובץ ← שמירה ← Run (buildSurvey) ← לאשר הרשאות.
 * בסוף, ב-Execution log: קישור להפצה, קישור לעריכה וקישור לגיליון התשובות.
 */
function buildSurvey() {
  var form = FormApp.create('הטלפון והזמן שלנו - סקר קצר');
  form.setDescription(
    'סקר של 4 דקות על הטלפון והזמן שלנו.\n' +
    'הסקר אנונימי לגמרי: לא נאספים שם, מייל או פרטי קשר.\n' +
    'אין תשובות נכונות. תשובה כנה עוזרת לנו הרבה יותר מתשובה נחמדה 🙏'
  );
  form.setProgressBar(true);
  form.setConfirmationMessage(
    'תודה רבה!\n' +
    'אם יש לך חבר/ה שגם מרגיש/ה שהטלפון לוקח יותר מדי זמן, נשמח שתעביר/י לו/ה את הסקר 🙏'
  );

  var SCREEN_RANGES = ['פחות מ-2 שעות', '2-3 שעות', '3-4 שעות', '4-5 שעות', '5-6 שעות', 'יותר מ-6 שעות'];

  function atMost(n) {
    return FormApp.createCheckboxValidation()
      .setHelpText('אפשר לבחור עד ' + n)
      .requireSelectAtMost(n)
      .build();
  }

  // ---------- חלק 1: הטלפון שלך ----------
  form.addSectionHeaderItem().setTitle('הטלפון שלך');

  form.addMultipleChoiceItem().setTitle('איזה טלפון יש לך?').setRequired(true)
    .setChoiceValues(['אנדרואיד (סמסונג, שיאומי, פיקסל וכו\')', 'אייפון', 'אחר']);

  form.addMultipleChoiceItem().setTitle('כמה זמן מסך יש לך ביום, לדעתך?')
    .setHelpText('זמן מסך = כל הזמן שהטלפון פתוח ואת/ה משתמש/ת בו.')
    .setRequired(true)
    .setChoiceValues(SCREEN_RANGES);

  form.addMultipleChoiceItem().setTitle('בדיקה של 30 שניות: כמה זה בפועל?')
    .setHelpText('אנדרואיד: הגדרות ← רווחה דיגיטלית. אייפון: הגדרות ← זמן מסך. הממוצע היומי.')
    .setRequired(true)
    .setChoiceValues(SCREEN_RANGES.concat(['לא בדקתי']));

  form.addCheckboxItem().setTitle('אילו אפליקציות לוקחות לך הכי הרבה זמן? (עד 3)').setRequired(true)
    .setValidation(atMost(3))
    .setChoiceValues(['אינסטגרם', 'טיקטוק', 'פייסבוק', 'יוטיוב', 'וואטסאפ', 'X (טוויטר)', 'אתרי חדשות', 'משחקים', 'נטפליקס / סטרימינג'])
    .showOtherOption(true);

  form.addCheckboxItem().setTitle('באילו רגעים את/ה הכי גולל/ת? (עד 3)').setRequired(true)
    .setValidation(atMost(3))
    .setChoiceValues([
      'מיד כשאני מתעורר/ת',
      'בעבודה, כשקשה או משעמם',
      'בהמתנה או בדרך',
      'אחרי העבודה, כדי להתנתק',
      'במיטה לפני השינה',
      'כשאני עם אנשים'
    ])
    .showOtherOption(true);

  form.addMultipleChoiceItem().setTitle('כמה מהזמן שלך ברשתות החברתיות הוא לצורכי עבודה?').setRequired(true)
    .setChoiceValues(['כמעט כלום', 'מעט', 'בערך חצי', 'רובו']);

  // ---------- חלק 2: מה זה עושה לך ----------
  form.addPageBreakItem().setTitle('מה זה עושה לך');

  form.addScaleItem().setTitle('עד כמה את/ה מרוצה מהזמן שאת/ה מבלה בטלפון?')
    .setBounds(1, 5).setLabels('בכלל לא מרוצה', 'מאוד מרוצה').setRequired(true);

  form.addCheckboxItem().setTitle('מה הכי מפריע לך בזה? (עד 2)').setRequired(true)
    .setValidation(atMost(2))
    .setChoiceValues([
      'זמן שהולך לאיבוד',
      'פגיעה בריכוז ובפרודוקטיביות',
      'פגיעה בשינה',
      'מצב רוח, השוואה לאחרים',
      'פחות זמן עם אנשים קרובים',
      'שום דבר לא מפריע לי'
    ]);

  form.addParagraphTextItem()
    .setTitle('ספר/י על הפעם האחרונה שהרגשת שבזבזת יותר מדי זמן בטלפון. מה קרה?')
    .setHelpText('לא חובה, אבל זה עוזר לנו מאוד.')
    .setRequired(false);

  // ---------- חלק 3: מה ניסית ----------
  form.addPageBreakItem().setTitle('מה ניסית');

  form.addCheckboxItem().setTitle('מה ניסית כדי לצמצם? (אפשר כמה)').setRequired(true)
    .setChoiceValues([
      'הגבלה מובנית בטלפון (זמן מסך / רווחה דיגיטלית)',
      'אפליקציה ייעודית (Opal, one sec, מוח וכו\')',
      'מחיקת אפליקציות',
      'טלפון פשוט / כשר',
      'כוח רצון',
      'לא ניסיתי'
    ])
    .showOtherOption(true);

  form.addMultipleChoiceItem().setTitle('כמה זמן זה החזיק?').setRequired(true)
    .setChoiceValues(['לא ניסיתי', 'פחות משבוע', '1-4 שבועות', '1-3 חודשים', 'עדיין עובד לי']);

  form.addMultipleChoiceItem().setTitle('למה זה הפסיק לעבוד? (הסיבה העיקרית)').setRequired(true)
    .setChoiceValues([
      'היה קל מדי לעקוף',
      'הרגיש מגביל ומעצבן מדי',
      'איבדתי מוטיבציה',
      'הייתי צריך/ה את הטלפון לעבודה',
      'זה עדיין עובד לי',
      'לא ניסיתי'
    ])
    .showOtherOption(true);

  // ---------- חלק 4: מה היה עובד לך ----------
  form.addPageBreakItem().setTitle('מה היה עובד לך');

  form.addMultipleChoiceItem().setTitle('כשנגמר הזמן שהקצבת לרשתות, מה היית רוצה שיקרה?').setRequired(true)
    .setChoiceValues([
      'רק תזכורת',
      'עצירה של כמה שניות ושאלה "בטוח?"',
      'חסימה עד מחר, שאפשר לעקוף במאמץ',
      'חסימה מוחלטת עד מחר',
      'שמישהו שבחרתי יקבל עדכון',
      'לא הייתי רוצה מגבלה'
    ]);

  form.addMultipleChoiceItem()
    .setTitle('היית מסכים/ה שחבר/ה, בן/בת זוג או מאמן/ת יראו את הזמן שלך ברשתות, כדי לעזור לך לעמוד ביעד?')
    .setRequired(true)
    .setChoiceValues(['כן', 'אולי', 'לא']);

  form.addMultipleChoiceItem().setTitle('מה הכי היה גורם לך להתמיד?').setRequired(true)
    .setChoiceValues([
      'לראות התקדמות ורצף ימים',
      'אתגר מול חברים',
      'מאמן/ת (אדם או AI) שמדבר/ת איתי על זה',
      'לראות מה זה עושה לשינה ולריכוז שלי',
      'פרס כשאני עומד/ת ביעד'
    ])
    .showOtherOption(true);

  // ---------- חלק 5: תשלום ----------
  form.addPageBreakItem().setTitle('תשלום');

  form.addMultipleChoiceItem()
    .setTitle('בשנה האחרונה, שילמת על אפליקציה, קורס או מאמן/ת כדי לשפר הרגל? (כושר, תזונה, למידה, מדיטציה וכו\')')
    .setRequired(true)
    .setChoiceValues(['לא', 'כן, עד 50 ₪ בחודש', 'כן, 50-150 ₪ בחודש', 'כן, יותר מ-150 ₪ בחודש']);

  form.addMultipleChoiceItem()
    .setTitle('אם אפליקציה באמת הייתה מורידה לך את הזמן ברשתות משמעותית, כמה היה הוגן לשלם בחודש?')
    .setRequired(true)
    .setChoiceValues(['0 ₪', 'עד 15 ₪', '15-30 ₪', '30-50 ₪', 'יותר מ-50 ₪']);

  // ---------- חלק 6: עליך ----------
  form.addPageBreakItem().setTitle('קצת עליך');

  form.addMultipleChoiceItem().setTitle('גיל').setRequired(true)
    .setChoiceValues(['18-24', '25-34', '35-44', '45-54', '55+']);

  form.addMultipleChoiceItem().setTitle('מצב תעסוקתי').setRequired(true)
    .setChoiceValues(['שכיר/ה', 'עצמאי/ת או בעל/ת עסק', 'סטודנט/ית', 'חייל/ת', 'לא עובד/ת כרגע', 'פנסיונר/ית']);

  form.addCheckboxItem().setTitle('מה עוד נכון לגביך? (אפשר כמה)').setRequired(false)
    .setChoiceValues([
      'הורה לילדים עד גיל 12',
      'מתאמן/ת 3 פעמים בשבוע ומעלה',
      'בתהליך התפתחות אישית (אימון, קורסים, טיפול)',
      'עובד/ת בעיקר מהבית',
      'אף אחד מאלה'
    ]);

  form.addMultipleChoiceItem().setTitle('מגדר').setRequired(false)
    .setChoiceValues(['גבר', 'אישה', 'מעדיף/ה לא לענות']);

  // ---------- גיליון תשובות ופרסום ----------
  var ss = SpreadsheetApp.create('תשובות - הטלפון והזמן שלנו');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // טפסים חדשים עשויים להיווצר במצב "לא פורסם"; מפרסמים ופותחים לתשובות
  try { if (typeof form.setPublished === 'function') form.setPublished(true); } catch (e) {}
  form.setAcceptingResponses(true);

  Logger.log('קישור להפצה: ' + form.getPublishedUrl());
  Logger.log('עריכת הטופס: ' + form.getEditUrl());
  Logger.log('גיליון התשובות: ' + ss.getUrl());
}
