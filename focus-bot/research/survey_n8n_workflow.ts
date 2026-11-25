import { workflow, node, trigger, expr } from '@n8n/workflow-sdk';

const page1 = trigger({
  type: 'n8n-nodes-base.formTrigger',
  version: 2.6,
  config: {
    name: "Page 1 - Phone",
    parameters: {
      formTitle: 'הטלפון והזמן שלנו',
      formDescription: "סקר של 4 דקות על הטלפון והזמן שלנו.<br>הסקר אנונימי לגמרי: לא נאספים שם, מייל או פרטי קשר.<br>אין תשובות נכונות. תשובה כנה עוזרת לנו הרבה יותר מתשובה נחמדה 🙏<br><br><b>חלק 1 מתוך 6: הטלפון שלך</b>",
      formFields: { values: [{"fieldLabel": "איזה טלפון יש לך?", "fieldName": "phone", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "אנדרואיד (סמסונג, שיאומי, פיקסל וכו')"}, {"option": "אייפון"}, {"option": "אחר"}]}}, {"fieldLabel": "כמה זמן מסך יש לך ביום, לדעתך? (כל הזמן שאת/ה משתמש/ת בטלפון)", "fieldName": "screen_estimate", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "פחות מ-2 שעות"}, {"option": "2-3 שעות"}, {"option": "3-4 שעות"}, {"option": "4-5 שעות"}, {"option": "5-6 שעות"}, {"option": "יותר מ-6 שעות"}]}}, {"fieldLabel": "בדיקה של 30 שניות: כמה זה בפועל? (אנדרואיד: הגדרות ← רווחה דיגיטלית. אייפון: הגדרות ← זמן מסך. הממוצע היומי)", "fieldName": "screen_actual", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "פחות מ-2 שעות"}, {"option": "2-3 שעות"}, {"option": "3-4 שעות"}, {"option": "4-5 שעות"}, {"option": "5-6 שעות"}, {"option": "יותר מ-6 שעות"}, {"option": "לא בדקתי"}]}}, {"fieldLabel": "אילו אפליקציות לוקחות לך הכי הרבה זמן? (עד 3)", "fieldName": "top_apps", "fieldType": "checkbox", "requiredField": true, "fieldOptions": {"values": [{"option": "אינסטגרם"}, {"option": "טיקטוק"}, {"option": "פייסבוק"}, {"option": "יוטיוב"}, {"option": "וואטסאפ"}, {"option": "X (טוויטר)"}, {"option": "אתרי חדשות"}, {"option": "משחקים"}, {"option": "נטפליקס / סטרימינג"}, {"option": "אחר"}]}, "limitSelection": "range", "minSelections": 1, "maxSelections": 3}, {"fieldLabel": "באילו רגעים את/ה הכי גולל/ת? (עד 3)", "fieldName": "scroll_moments", "fieldType": "checkbox", "requiredField": true, "fieldOptions": {"values": [{"option": "מיד כשאני מתעורר/ת"}, {"option": "בעבודה, כשקשה או משעמם"}, {"option": "בהמתנה או בדרך"}, {"option": "אחרי העבודה, כדי להתנתק"}, {"option": "במיטה לפני השינה"}, {"option": "כשאני עם אנשים"}, {"option": "אחר"}]}, "limitSelection": "range", "minSelections": 1, "maxSelections": 3}, {"fieldLabel": "כמה מהזמן שלך ברשתות החברתיות הוא לצורכי עבודה?", "fieldName": "work_share", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "כמעט כלום"}, {"option": "מעט"}, {"option": "בערך חצי"}, {"option": "רובו"}]}}] },
      options: { appendAttribution: false, buttonLabel: 'המשך', path: 'phone-time-survey', customCss: "html, body, form, .card, .form-group, label, p, h1, h2, input, textarea, select { direction: rtl; text-align: right; } .checkbox-label, .radio-label, .multiselect-option { direction: rtl; }", ignoreBots: true }
    },
    position: [240, 300]
  },
  output: [{"phone": "x", "screen_estimate": "x", "screen_actual": "x", "top_apps": "x", "scroll_moments": "x", "work_share": "x", "submittedAt": "2026-11-25T10:00:00.000+02:00"}]
});

const page2 = node({
  type: 'n8n-nodes-base.form',
  version: 2.5,
  config: {
    name: "Page 2 - Impact",
    parameters: {
      operation: 'page',
      defineForm: 'fields',
      formFields: { values: [{"fieldLabel": "עד כמה את/ה מרוצה מהזמן שאת/ה מבלה בטלפון?", "fieldName": "satisfaction", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "1 - בכלל לא מרוצה"}, {"option": "2"}, {"option": "3"}, {"option": "4"}, {"option": "5 - מאוד מרוצה"}]}}, {"fieldLabel": "מה הכי מפריע לך בזה? (עד 2)", "fieldName": "bothers", "fieldType": "checkbox", "requiredField": true, "fieldOptions": {"values": [{"option": "זמן שהולך לאיבוד"}, {"option": "פגיעה בריכוז ובפרודוקטיביות"}, {"option": "פגיעה בשינה"}, {"option": "מצב רוח, השוואה לאחרים"}, {"option": "פחות זמן עם אנשים קרובים"}, {"option": "שום דבר לא מפריע לי"}]}, "limitSelection": "range", "minSelections": 1, "maxSelections": 2}, {"fieldLabel": "ספר/י על הפעם האחרונה שהרגשת שבזבזת יותר מדי זמן בטלפון. מה קרה? (לא חובה, אבל זה עוזר לנו מאוד)", "fieldName": "last_time_story", "fieldType": "textarea", "requiredField": false, "placeholder": "כמה מילים זה מספיק"}] },
      options: { formTitle: 'הטלפון והזמן שלנו', formDescription: "<b>חלק 2 מתוך 6: מה זה עושה לך</b>", buttonLabel: "המשך", appendAttribution: false, customCss: "html, body, form, .card, .form-group, label, p, h1, h2, input, textarea, select { direction: rtl; text-align: right; } .checkbox-label, .radio-label, .multiselect-option { direction: rtl; }" }
    },
    position: [760, 300]
  },
  output: [{"satisfaction": "x", "bothers": "x", "last_time_story": "x"}]
});

const page3 = node({
  type: 'n8n-nodes-base.form',
  version: 2.5,
  config: {
    name: "Page 3 - Attempts",
    parameters: {
      operation: 'page',
      defineForm: 'fields',
      formFields: { values: [{"fieldLabel": "מה ניסית כדי לצמצם? (אפשר כמה)", "fieldName": "tried", "fieldType": "checkbox", "requiredField": true, "fieldOptions": {"values": [{"option": "הגבלה מובנית בטלפון (זמן מסך / רווחה דיגיטלית)"}, {"option": "אפליקציה ייעודית (Opal, one sec, מוח וכו')"}, {"option": "מחיקת אפליקציות"}, {"option": "טלפון פשוט / כשר"}, {"option": "כוח רצון"}, {"option": "אחר"}, {"option": "לא ניסיתי"}]}}, {"fieldLabel": "כמה זמן זה החזיק?", "fieldName": "lasted", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "לא ניסיתי"}, {"option": "פחות משבוע"}, {"option": "1-4 שבועות"}, {"option": "1-3 חודשים"}, {"option": "עדיין עובד לי"}]}}, {"fieldLabel": "למה זה הפסיק לעבוד? (הסיבה העיקרית)", "fieldName": "why_stopped", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "היה קל מדי לעקוף"}, {"option": "הרגיש מגביל ומעצבן מדי"}, {"option": "איבדתי מוטיבציה"}, {"option": "הייתי צריך/ה את הטלפון לעבודה"}, {"option": "זה עדיין עובד לי"}, {"option": "לא ניסיתי"}, {"option": "אחר"}]}}] },
      options: { formTitle: 'הטלפון והזמן שלנו', formDescription: "<b>חלק 3 מתוך 6: מה ניסית</b>", buttonLabel: "המשך", appendAttribution: false, customCss: "html, body, form, .card, .form-group, label, p, h1, h2, input, textarea, select { direction: rtl; text-align: right; } .checkbox-label, .radio-label, .multiselect-option { direction: rtl; }" }
    },
    position: [1020, 300]
  },
  output: [{"tried": "x", "lasted": "x", "why_stopped": "x"}]
});

const page4 = node({
  type: 'n8n-nodes-base.form',
  version: 2.5,
  config: {
    name: "Page 4 - Preferences",
    parameters: {
      operation: 'page',
      defineForm: 'fields',
      formFields: { values: [{"fieldLabel": "כשנגמר הזמן שהקצבת לרשתות, מה היית רוצה שיקרה?", "fieldName": "at_limit", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "רק תזכורת"}, {"option": "עצירה של כמה שניות ושאלה \"בטוח?\""}, {"option": "חסימה עד מחר, שאפשר לעקוף במאמץ"}, {"option": "חסימה מוחלטת עד מחר"}, {"option": "שמישהו שבחרתי יקבל עדכון"}, {"option": "לא הייתי רוצה מגבלה"}]}}, {"fieldLabel": "היית מסכים/ה שחבר/ה, בן/בת זוג או מאמן/ת יראו את הזמן שלך ברשתות, כדי לעזור לך לעמוד ביעד?", "fieldName": "accountability", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "כן"}, {"option": "אולי"}, {"option": "לא"}]}}, {"fieldLabel": "מה הכי היה גורם לך להתמיד?", "fieldName": "persist_driver", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "לראות התקדמות ורצף ימים"}, {"option": "אתגר מול חברים"}, {"option": "מאמן/ת (אדם או AI) שמדבר/ת איתי על זה"}, {"option": "לראות מה זה עושה לשינה ולריכוז שלי"}, {"option": "פרס כשאני עומד/ת ביעד"}, {"option": "אחר"}]}}] },
      options: { formTitle: 'הטלפון והזמן שלנו', formDescription: "<b>חלק 4 מתוך 6: מה היה עובד לך</b>", buttonLabel: "המשך", appendAttribution: false, customCss: "html, body, form, .card, .form-group, label, p, h1, h2, input, textarea, select { direction: rtl; text-align: right; } .checkbox-label, .radio-label, .multiselect-option { direction: rtl; }" }
    },
    position: [1280, 300]
  },
  output: [{"at_limit": "x", "accountability": "x", "persist_driver": "x"}]
});

const page5 = node({
  type: 'n8n-nodes-base.form',
  version: 2.5,
  config: {
    name: "Page 5 - Payment",
    parameters: {
      operation: 'page',
      defineForm: 'fields',
      formFields: { values: [{"fieldLabel": "בשנה האחרונה, שילמת על אפליקציה, קורס או מאמן/ת כדי לשפר הרגל? (כושר, תזונה, למידה, מדיטציה וכו')", "fieldName": "paid_last_year", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "לא"}, {"option": "כן, עד 50 ₪ בחודש"}, {"option": "כן, 50-150 ₪ בחודש"}, {"option": "כן, יותר מ-150 ₪ בחודש"}]}}, {"fieldLabel": "אם אפליקציה באמת הייתה מורידה לך את הזמן ברשתות משמעותית, כמה היה הוגן לשלם בחודש?", "fieldName": "fair_price", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "0 ₪"}, {"option": "עד 15 ₪"}, {"option": "15-30 ₪"}, {"option": "30-50 ₪"}, {"option": "יותר מ-50 ₪"}]}}] },
      options: { formTitle: 'הטלפון והזמן שלנו', formDescription: "<b>חלק 5 מתוך 6: תשלום</b>", buttonLabel: "המשך", appendAttribution: false, customCss: "html, body, form, .card, .form-group, label, p, h1, h2, input, textarea, select { direction: rtl; text-align: right; } .checkbox-label, .radio-label, .multiselect-option { direction: rtl; }" }
    },
    position: [1540, 300]
  },
  output: [{"paid_last_year": "x", "fair_price": "x"}]
});

const page6 = node({
  type: 'n8n-nodes-base.form',
  version: 2.5,
  config: {
    name: "Page 6 - About",
    parameters: {
      operation: 'page',
      defineForm: 'fields',
      formFields: { values: [{"fieldLabel": "גיל", "fieldName": "age", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "18-24"}, {"option": "25-34"}, {"option": "35-44"}, {"option": "45-54"}, {"option": "55+"}]}}, {"fieldLabel": "מצב תעסוקתי", "fieldName": "employment", "fieldType": "radio", "requiredField": true, "fieldOptions": {"values": [{"option": "שכיר/ה"}, {"option": "עצמאי/ת או בעל/ת עסק"}, {"option": "סטודנט/ית"}, {"option": "חייל/ת"}, {"option": "לא עובד/ת כרגע"}, {"option": "פנסיונר/ית"}]}}, {"fieldLabel": "מה עוד נכון לגביך? (אפשר כמה, לא חובה)", "fieldName": "life_context", "fieldType": "checkbox", "requiredField": false, "fieldOptions": {"values": [{"option": "הורה לילדים עד גיל 12"}, {"option": "מתאמן/ת 3 פעמים בשבוע ומעלה"}, {"option": "בתהליך התפתחות אישית (אימון, קורסים, טיפול)"}, {"option": "עובד/ת בעיקר מהבית"}, {"option": "אף אחד מאלה"}]}}, {"fieldLabel": "מגדר (לא חובה)", "fieldName": "gender", "fieldType": "radio", "requiredField": false, "fieldOptions": {"values": [{"option": "גבר"}, {"option": "אישה"}, {"option": "מעדיף/ה לא לענות"}]}}] },
      options: { formTitle: 'הטלפון והזמן שלנו', formDescription: "<b>חלק 6 מתוך 6: קצת עליך</b>", buttonLabel: "שליחה", appendAttribution: false, customCss: "html, body, form, .card, .form-group, label, p, h1, h2, input, textarea, select { direction: rtl; text-align: right; } .checkbox-label, .radio-label, .multiselect-option { direction: rtl; }" }
    },
    position: [1800, 300]
  },
  output: [{"age": "x", "employment": "x", "life_context": "x", "gender": "x"}]
});

const collect = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Collect Answers',
    parameters: { mode: 'runOnceForAllItems', jsCode: "const pageNodes = [\"Page 1 - Phone\", \"Page 2 - Impact\", \"Page 3 - Attempts\", \"Page 4 - Preferences\", \"Page 5 - Payment\", \"Page 6 - About\"];\nconst cols = [\"submitted_at\", \"phone\", \"screen_estimate\", \"screen_actual\", \"top_apps\", \"scroll_moments\", \"work_share\", \"satisfaction\", \"bothers\", \"last_time_story\", \"tried\", \"lasted\", \"why_stopped\", \"at_limit\", \"accountability\", \"persist_driver\", \"paid_last_year\", \"fair_price\", \"age\", \"employment\", \"life_context\", \"gender\"];\nconst byLabel = {\"איזה טלפון יש לך?\": \"phone\", \"כמה זמן מסך יש לך ביום, לדעתך? (כל הזמן שאת/ה משתמש/ת בטלפון)\": \"screen_estimate\", \"בדיקה של 30 שניות: כמה זה בפועל? (אנדרואיד: הגדרות ← רווחה דיגיטלית. אייפון: הגדרות ← זמן מסך. הממוצע היומי)\": \"screen_actual\", \"אילו אפליקציות לוקחות לך הכי הרבה זמן? (עד 3)\": \"top_apps\", \"באילו רגעים את/ה הכי גולל/ת? (עד 3)\": \"scroll_moments\", \"כמה מהזמן שלך ברשתות החברתיות הוא לצורכי עבודה?\": \"work_share\", \"עד כמה את/ה מרוצה מהזמן שאת/ה מבלה בטלפון?\": \"satisfaction\", \"מה הכי מפריע לך בזה? (עד 2)\": \"bothers\", \"ספר/י על הפעם האחרונה שהרגשת שבזבזת יותר מדי זמן בטלפון. מה קרה? (לא חובה, אבל זה עוזר לנו מאוד)\": \"last_time_story\", \"מה ניסית כדי לצמצם? (אפשר כמה)\": \"tried\", \"כמה זמן זה החזיק?\": \"lasted\", \"למה זה הפסיק לעבוד? (הסיבה העיקרית)\": \"why_stopped\", \"כשנגמר הזמן שהקצבת לרשתות, מה היית רוצה שיקרה?\": \"at_limit\", \"היית מסכים/ה שחבר/ה, בן/בת זוג או מאמן/ת יראו את הזמן שלך ברשתות, כדי לעזור לך לעמוד ביעד?\": \"accountability\", \"מה הכי היה גורם לך להתמיד?\": \"persist_driver\", \"בשנה האחרונה, שילמת על אפליקציה, קורס או מאמן/ת כדי לשפר הרגל? (כושר, תזונה, למידה, מדיטציה וכו')\": \"paid_last_year\", \"אם אפליקציה באמת הייתה מורידה לך את הזמן ברשתות משמעותית, כמה היה הוגן לשלם בחודש?\": \"fair_price\", \"גיל\": \"age\", \"מצב תעסוקתי\": \"employment\", \"מה עוד נכון לגביך? (אפשר כמה, לא חובה)\": \"life_context\", \"מגדר (לא חובה)\": \"gender\"};\nconst row = {};\nfor (const n of pageNodes) {\n  const j = $(n).first().json || {};\n  for (const k of Object.keys(j)) {\n    const col = cols.includes(k) ? k : byLabel[k];\n    if (!col || col === 'submitted_at') continue;\n    const v = j[k];\n    row[col] = Array.isArray(v) ? v.join(' | ') : (v === null || v === undefined ? '' : String(v));\n  }\n}\nrow.submitted_at = ($(pageNodes[0]).first().json || {}).submittedAt || new Date().toISOString();\nfor (const c of cols) { if (!(c in row)) row[c] = ''; }\nreturn [{ json: row }];" },
    position: [2060, 300]
  },
  output: [{"submitted_at": "x", "phone": "x", "screen_estimate": "x", "screen_actual": "x", "top_apps": "x", "scroll_moments": "x", "work_share": "x", "satisfaction": "x", "bothers": "x", "last_time_story": "x", "tried": "x", "lasted": "x", "why_stopped": "x", "at_limit": "x", "accountability": "x", "persist_driver": "x", "paid_last_year": "x", "fair_price": "x", "age": "x", "employment": "x", "life_context": "x", "gender": "x"}]
});

const store = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Save Response',
    parameters: {
      resource: 'row',
      operation: 'insert',
      dataTableId: { __rl: true, mode: 'id', value: 'A99STo5b1gyWW1CB', cachedResultName: 'survey_phone_time' },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          submitted_at: expr('{{ $json.submitted_at }}'),
          phone: expr('{{ $json.phone }}'),
          screen_estimate: expr('{{ $json.screen_estimate }}'),
          screen_actual: expr('{{ $json.screen_actual }}'),
          top_apps: expr('{{ $json.top_apps }}'),
          scroll_moments: expr('{{ $json.scroll_moments }}'),
          work_share: expr('{{ $json.work_share }}'),
          satisfaction: expr('{{ $json.satisfaction }}'),
          bothers: expr('{{ $json.bothers }}'),
          last_time_story: expr('{{ $json.last_time_story }}'),
          tried: expr('{{ $json.tried }}'),
          lasted: expr('{{ $json.lasted }}'),
          why_stopped: expr('{{ $json.why_stopped }}'),
          at_limit: expr('{{ $json.at_limit }}'),
          accountability: expr('{{ $json.accountability }}'),
          persist_driver: expr('{{ $json.persist_driver }}'),
          paid_last_year: expr('{{ $json.paid_last_year }}'),
          fair_price: expr('{{ $json.fair_price }}'),
          age: expr('{{ $json.age }}'),
          employment: expr('{{ $json.employment }}'),
          life_context: expr('{{ $json.life_context }}'),
          gender: expr('{{ $json.gender }}')
        },
        schema: [{"id": "submitted_at", "displayName": "submitted_at", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "phone", "displayName": "phone", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "screen_estimate", "displayName": "screen_estimate", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "screen_actual", "displayName": "screen_actual", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "top_apps", "displayName": "top_apps", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "scroll_moments", "displayName": "scroll_moments", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "work_share", "displayName": "work_share", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "satisfaction", "displayName": "satisfaction", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "bothers", "displayName": "bothers", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "last_time_story", "displayName": "last_time_story", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "tried", "displayName": "tried", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "lasted", "displayName": "lasted", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "why_stopped", "displayName": "why_stopped", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "at_limit", "displayName": "at_limit", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "accountability", "displayName": "accountability", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "persist_driver", "displayName": "persist_driver", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "paid_last_year", "displayName": "paid_last_year", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "fair_price", "displayName": "fair_price", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "age", "displayName": "age", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "employment", "displayName": "employment", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "life_context", "displayName": "life_context", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}, {"id": "gender", "displayName": "gender", "required": false, "defaultMatch": false, "display": true, "type": "string", "canBeUsedToMatch": true}]
      }
    },
    position: [2320, 300]
  },
  output: [{ id: 1, createdAt: '2026-11-25T10:00:00.000Z', updatedAt: '2026-11-25T10:00:00.000Z' }]
});

const done = node({
  type: 'n8n-nodes-base.form',
  version: 2.5,
  config: {
    name: 'Thank You',
    parameters: {
      operation: 'completion',
      respondWith: 'text',
      completionTitle: 'תודה רבה!',
      completionMessage: 'התשובות נשמרו. אם יש לך חבר/ה שגם מרגיש/ה שהטלפון לוקח יותר מדי זמן, נשמח שתעביר/י לו/ה את הסקר 🙏'
    },
    position: [2580, 300]
  },
  output: [{}]
});

export default workflow('phone-time-survey', 'סקר: הטלפון והזמן שלנו')
  .add(page1)
  .to(page2)
  .to(page3)
  .to(page4)
  .to(page5)
  .to(page6)
  .to(collect)
  .to(store)
  .to(done)
  .group('Survey pages', [page2, page3, page4, page5, page6], { description: 'Pages 2-6 of the anonymous survey' })
  .group('Save', [collect, store], { description: 'Flatten all answers into one row and save to the survey_phone_time data table' });
