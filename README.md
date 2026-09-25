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

## Run On A Python Host

The dashboard is a standard Python HTTP server and can run on any host that
supports Python 3.10 or newer. For a managed host such as Render or Railway,
use this start command:

```powershell
python solution/app.py --month --serve --host 0.0.0.0 --port $PORT
```

For local development, use port 8000 instead:

```powershell
python solution/app.py --month --serve --host 127.0.0.1 --port 8000
```

## Deploy To Render

The repository includes `render.yaml`, so Render can configure the service
automatically from the repository.

1. Push the repository to GitHub.
2. In Render, choose **New + -> Blueprint**.
3. Select this repository and apply the blueprint.
4. Render uses the included build command, start command, free plan, and
	`/api/live` health check.

The service starts with the 30-day bookstore replay and listens on Render's
assigned `$PORT`.

## Deploy To PythonAnywhere

The repository includes `pythonanywhere_wsgi.py`, a WSGI entry point for the
PythonAnywhere Web tab.

1. Upload or clone this repository into `/home/<username>/finals-team-05`.
2. Create a Python 3.10+ web app from the PythonAnywhere Web tab.
3. Set the WSGI file to:
	`/home/<username>/finals-team-05/pythonanywhere_wsgi.py`.
4. Set the source directory to:
	`/home/<username>/finals-team-05`.
5. Reload the web app.

No package installation is required. The dashboard is available at the
PythonAnywhere application URL, with JSON available at `/api/live` and
`/api/incident`. Use `/api/live?mode=original` for the supplied six-hour
replay.