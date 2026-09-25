# Outage Watch

I built Outage Watch to detect and explain cascading failures in a bookstore
microservice platform. It replays supplied telemetry, supports a deterministic
30-day hourly simulation, follows the service dependency graph, and ranks
configuration changes as likely causes.

## Structure

```text
datasets/          input CSV and JSON streams
sabotage_drops/    optional live replacement streams
solution/          detector, graph analysis, report generator, dashboard
reports/           generated Markdown and JSON output
demo/              local demo instructions
```

## Run

From the repository root:

```powershell
python solution/app.py --report
python solution/app.py --serve --port 8000
```

The first command writes `reports/incident_report.md` and
`reports/incident.json`. The second opens a local dashboard at
`http://127.0.0.1:8000`.

The detector uses a median/MAD baseline, a rolling latency trend, and reverse
dependency traversal. This avoids treating a single noisy spike as an
incident and identifies the upstream service rather than the most degraded
downstream service. The dashboard also supports daily incident review,
interactive dependency graphs, failed-service blast-radius analysis, and a
calendar-filtered analyst queue.