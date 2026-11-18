import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
PHONE_TOKEN = os.environ.get("PHONE_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-5-5")
TZ = ZoneInfo(os.environ.get("TZ", "Asia/Jerusalem"))
PORT = int(os.environ.get("PORT", "8080"))
DB_PATH = os.environ.get("DB_PATH", "data/focus.db")

DEFAULT_TOTAL_LIMIT = int(os.environ.get("DAILY_LIMIT_MIN", "120"))
DEFAULT_SOCIAL_LIMIT = int(os.environ.get("SOCIAL_LIMIT_MIN", "45"))
SOCIAL_APPS = [
    a.strip().lower()
    for a in os.environ.get(
        "SOCIAL_APPS", "Instagram,TikTok,Facebook,X,Twitter,Snapchat,YouTube,Reddit,Threads"
    ).split(",")
    if a.strip()
]

MORNING_TIME = os.environ.get("MORNING_TIME", "08:00")
CHECKIN_TIMES = [t.strip() for t in os.environ.get("CHECKIN_TIMES", "10:30,13:00,15:30,18:00,20:30").split(",") if t.strip()]
EVENING_TIME = os.environ.get("EVENING_TIME", "21:30")
CHECKIN_TIMEOUT_MIN = int(os.environ.get("CHECKIN_TIMEOUT_MIN", "20"))
SESSION_NOTIFY_MIN = float(os.environ.get("SESSION_NOTIFY_MIN", "5"))  # תגובה מיידית על כל שהייה ארוכה מזה

# חבילות אנדרואיד שנחשבות "רשתות חברתיות" (לדיווח המדויק מ-Tasker). אפשר לדרוס ב-.env
_DEFAULT_SOCIAL_PACKAGES = (
    "com.instagram.android:Instagram,com.instagram.barcelona:Threads,"
    "com.facebook.katana:Facebook,com.facebook.lite:Facebook Lite,"
    "com.zhiliaoapp.musically:TikTok,com.ss.android.ugc.trill:TikTok,"
    "com.google.android.youtube:YouTube,com.twitter.android:X,"
    "com.snapchat.android:Snapchat,com.reddit.frontpage:Reddit"
)
SOCIAL_PACKAGES = dict(
    item.split(":", 1)
    for item in os.environ.get("SOCIAL_PACKAGES", _DEFAULT_SOCIAL_PACKAGES).split(",")
    if ":" in item
)
STATUS_DAY_START = os.environ.get("STATUS_DAY_START", "08:00")
STATUS_DAY_END = os.environ.get("STATUS_DAY_END", "23:00")
