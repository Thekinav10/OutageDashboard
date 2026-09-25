# Outage Watch

Outage Watch replays the supplied six-hour metrics stream, detects sustained
latency deterioration, follows the service dependency graph, and ranks nearby
configuration changes as likely causes.

## Structure

```text
datasets/          input CSV and JSON streams
sabotage_drops/    optional live replacement streams
solution/          detector, graph analysis, report generator, dashboard
reports/           generated Markdown and JSON output
demo/              judging/demo instructions
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
downstream service.