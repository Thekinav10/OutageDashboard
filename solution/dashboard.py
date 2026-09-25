"""Small zero-dependency browser dashboard for a replay result."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def render_dashboard(result: dict) -> str:
    cascade = result["cascade"]
    rows = "".join(f"<tr><td>{edge['timestamp_min']}</td><td>{edge['from']}</td><td>{edge['to']}</td><td>{edge['lag_min']} min</td></tr>" for edge in cascade.get("path", []))
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Outage Watch</title><style>body{{font:16px system-ui;margin:40px;background:#f4f1ea;color:#17211b}}main{{max-width:1000px;margin:auto}}.hero{{background:#173d35;color:#f4f1ea;padding:28px;border-radius:8px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0}}.card{{background:white;padding:18px;border-left:4px solid #d56b38}}table{{background:white;border-collapse:collapse;width:100%}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #ddd}}small{{color:#68756d}}</style></head><body><main><section class='hero'><small>HACKONEX / REPLAY MONITOR</small><h1>Slow cascade detected</h1><p>Graph-aware monitoring caught the failure before platform-wide outage.</p></section><section class='grid'><div class='card'><small>ROOT SERVICE</small><h2>{cascade.get('root_service','unknown')}</h2></div><div class='card'><small>EARLIEST SIGNAL</small><h2>Minute {result.get('earliest_detectable_min')}</h2></div><div class='card'><small>INTERVENE BY</small><h2>Minute {result.get('recommended_intervention_min')}</h2></div></section><h2>Propagation timeline</h2><table><tr><th>Minute</th><th>From</th><th>To</th><th>Lag</th></tr>{rows}</table><h2>Likely config change</h2><p><strong>{cascade.get('root_cause',{}).get('change_id','unknown')}</strong>: {cascade.get('root_cause',{}).get('description','unknown')}</p></main></body></html>"""


def serve(result: dict, host: str = "127.0.0.1", port: int = 8000) -> None:
    page = render_dashboard(result).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/api/incident":
                payload = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
        def log_message(self, *_args):
            return

    print(f"Dashboard: http://{host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()
