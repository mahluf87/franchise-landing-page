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
    total_limit, social_limit = db.limits()
    usage = db.usage_range(days)
    rate = db.task_rate(days)
    today = datetime.now(config.TZ).date()
    day_list = [(today - timedelta(days=i)) for i in range(days - 1, -1, -1)]
    labels = [d.strftime("%d/%m") for d in day_list]
    keys = [d.isoformat() for d in day_list]

    total = [usage.get(k, {}).get("total_min", 0) for k in keys]
    social = [usage.get(k, {}).get("social_min", 0) for k in keys]
    colors = ["#d64545" if t > total_limit else "#3ba55d" for t in total]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={"height_ratios": [3, 2]}, sharex=True)
    ax1.bar(labels, total, color=colors, label=heb("סך הכל"))
    ax1.bar(labels, social, color="#1f2d3d", width=0.4, label=heb("רשתות חברתיות"))
    ax1.axhline(total_limit, color="#d64545", ls="--", lw=1.2)
    ax1.axhline(social_limit, color="#1f2d3d", ls=":", lw=1.2)
    ax1.set_ylabel(heb("דקות"))
    ax1.set_title(heb("ימים אחרונים") + f" {days} " + heb("- זמן מסך") + "     " + heb("רצף ימים") + f": {db.streak()}")
    ax1.set_ylim(0, max(max(total, default=0), total_limit) * 1.25 or 1)
    ax1.legend(loc="upper left", ncol=2)
    ax1.grid(axis="y", alpha=0.3)

    pct = [rate.get(k) for k in keys]
    xs = [i for i, v in enumerate(pct) if v is not None]
    ys = [pct[i] for i in xs]
    ax2.plot([labels[i] for i in xs], ys, marker="o", color="#2b7de9")
    ax2.set_ylim(0, 105)
    ax2.set_ylabel(heb("משימות שבוצעו %"))
    ax2.grid(alpha=0.3)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130)
    plt.close(fig)
    return buf.getvalue()
