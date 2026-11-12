"""שרת HTTP קטן שמקבל דיווחי שימוש מהטלפון.

POST /usage  {"total_minutes":95,"social_minutes":40,"pickups":60,"apps":{"Instagram":25}, "date":"2026-11-12"}   (מצטבר ליום)
POST /event  {"app":"Instagram","minutes":3.5}                                                                   (הוספה בודדת)
GET  /health
כותרת חובה:  Authorization: Bearer <PHONE_TOKEN>
"""
import hmac
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import config, db

log = logging.getLogger(__name__)


def make_handler(on_update):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self):
            got = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
            return bool(config.PHONE_TOKEN) and hmac.compare_digest(got, config.PHONE_TOKEN)

        def do_GET(self):
            if self.path == "/health":
                return self._send(200, {"ok": True})
            self._send(404, {"error": "not found"})

        def do_POST(self):
            if not self._authorized():
                return self._send(401, {"error": "unauthorized"})
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n) or b"{}")
                day = data.get("date") or db.today()
                if self.path == "/usage":
                    db.set_usage(
                        day,
                        total_min=data.get("total_minutes"),
                        social_min=data.get("social_minutes"),
                        pickups=data.get("pickups"),
                        apps=data.get("apps"),
                    )
                elif self.path == "/event":
                    db.add_app_time(day, str(data["app"]), float(data["minutes"]))
                else:
                    return self._send(404, {"error": "not found"})
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                return self._send(400, {"error": str(e)})
            on_update(day)
            self._send(200, {"ok": True, "usage": db.get_usage(day)})

        def log_message(self, fmt, *args):  # שקט
            log.debug(fmt, *args)

    return Handler


def start(on_update):
    srv = ThreadingHTTPServer(("0.0.0.0", config.PORT), make_handler(on_update))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    log.info("usage server listening on :%s", config.PORT)
    return srv
