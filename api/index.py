"""Vercel serverless entry point for the Outage Watch dashboard."""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solution.app import run
from solution.dashboard import render_dashboard


class handler(BaseHTTPRequestHandler):
    """Serve a fresh replay result for each Vercel request."""

    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        month = query.get("mode", ["month"])[0] != "original"
        result = run(month=month)
        request_path = urlparse(self.path).path
        if request_path.endswith("/live") or request_path.endswith("/incident"):
            body = json.dumps(result).encode("utf-8")
            content_type = "application/json"
        else:
            body = render_dashboard(result).encode("utf-8")
            content_type = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args) -> None:
        return
