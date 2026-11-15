#!/usr/bin/env bash
# פריסה על VPS (Ubuntu/Debian). הרצה:  bash deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/4 בדיקת Docker =="
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker לא מותקן, מתקין..."
  curl -fsSL https://get.docker.com | sh
fi
docker compose version >/dev/null

echo "== 2/4 הגדרות =="
if [ -f .env ]; then
  echo "נמצא .env קיים, משתמש בו (מחק אותו אם אתה רוצה להגדיר מחדש)."
else
  read -r -s -p "טוקן הבוט מ-BotFather (ההקלדה מוסתרת): " BOT_TOKEN; echo
  [ -n "$BOT_TOKEN" ] || { echo "חסר טוקן"; exit 1; }
  DEFAULT_DOMAIN="$(hostname -f 2>/dev/null || hostname)"
  read -r -p "דומיין של השרת [$DEFAULT_DOMAIN]: " DOMAIN; DOMAIN="${DOMAIN:-$DEFAULT_DOMAIN}"
  read -r -s -p "מפתח Anthropic (אופציונלי, Enter לדילוג): " AKEY; echo
  PHONE_TOKEN="$(openssl rand -hex 24)"
  umask 077
  cat > .env <<ENV
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
PHONE_TOKEN=$PHONE_TOKEN
ANTHROPIC_API_KEY=$AKEY
TZ=Asia/Jerusalem
DOMAIN=$DOMAIN
ENV
fi

set -a; . ./.env; set +a

echo "== 3/4 בנייה והפעלה =="
docker compose up -d --build

echo "== 4/4 בדיקה (עד 60 שניות, ממתין לתעודת HTTPS) =="
ok=0
for _ in $(seq 1 12); do
  if curl -fsS "https://$DOMAIN/health" >/dev/null 2>&1; then ok=1; break; fi
  sleep 5
done

echo
if [ "$ok" = 1 ]; then
  echo "✅ השרת עונה ב-https://$DOMAIN/health"
else
  echo "⚠️ https://$DOMAIN/health עדיין לא עונה. בדוק: docker compose logs caddy bot"
fi
echo
echo "שמור את הפרטים האלה להגדרת MacroDroid:"
echo "  כתובת:  https://$DOMAIN"
echo "  PHONE_TOKEN: $PHONE_TOKEN"
echo
echo "עכשיו שלח /start לבוט בטלגרם."
