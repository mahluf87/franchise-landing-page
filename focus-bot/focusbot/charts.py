"""גרף התקדמות. ל-matplotlib אין תמיכה ב-RTL, לכן הכותרות העבריות מוהפכות ידנית."""
import io
from datetime import datetime, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import config, db  # noqa: E402


def heb(s: str) -> str:
    return s[::-1]


def build_report(days: int = 14) -> bytes:
    _, social_limit = db.limits()
    usage = db.usage_range(days)
    today = datetime.now(config.TZ).date()
    day_list = [(today - timedelta(days=i)) for i in range(days - 1, -1, -1)]
    labels = [d.strftime("%d/%m") for d in day_list]
    social = [usage.get(d.isoformat(), {}).get("social_min", 0) for d in day_list]
    colors = ["#d64545" if v > social_limit else "#3ba55d" for v in social]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(labels, social, color=colors)
    for bar, v in zip(bars, social):
        if v >= 1:
            ax.text(bar.get_x() + bar.get_width() / 2, v, f"{int(round(v))}", ha="center", va="bottom", fontsize=9)
    ax.axhline(social_limit, color="#1f2d3d", ls="--", lw=1.4)
    ax.text(len(labels) - 0.5, social_limit, f" {social_limit}", va="bottom", ha="right", fontsize=9, color="#1f2d3d")
    ax.set_ylabel(heb("דקות ברשתות"))
    ax.set_ylim(0, max(max(social, default=0), social_limit) * 1.25 or 1)
    ax.set_title(heb("ימים אחרונים") + f" {days} " + heb("- זמן ברשתות") + "     " + heb("רצף ימים") + f": {db.streak()}")
    ax.grid(axis="y", alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130)
    plt.close(fig)
    return buf.getvalue()
