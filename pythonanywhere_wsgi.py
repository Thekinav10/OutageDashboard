"""PythonAnywhere WSGI entry point for Outage Watch."""

import json
import sys
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solution.app import run
from solution.dashboard import render_dashboard

RESULT = run(month=True)


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    query = parse_qs(environ.get("QUERY_STRING", ""))
    result = RESULT
    if query.get("mode", ["month"])[0] == "original":
        result = run(month=False)

    if path.endswith("/live") or path.endswith("/incident"):
        body = json.dumps(result).encode("utf-8")
        content_type = "application/json"
    else:
        body = render_dashboard(result).encode("utf-8")
        content_type = "text/html; charset=utf-8"

    start_response("200 OK", [
        ("Content-Type", content_type),
        ("Cache-Control", "no-store"),
        ("Content-Length", str(len(body))),
    ])
    return [body]
