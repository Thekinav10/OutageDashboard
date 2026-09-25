## Run the outage replay

The replay uses the supplied CSV and JSON files and has no external service
dependencies.

```powershell
cd solution
python app.py --report
python app.py --serve --port 8000
```

Open `http://127.0.0.1:8000` for the live dashboard. The report is also
written to `reports/incident_report.md` and the machine-readable result to
`reports/incident.json`.

To replay a different drop, put replacement files in `sabotage_drops/` using
the same names as the files in `datasets/`, then run:

```powershell
python solution/app.py --data-dir sabotage_drops --report
```
