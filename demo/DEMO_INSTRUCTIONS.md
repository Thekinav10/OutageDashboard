## Run the project

I use the following commands to run the replay and dashboard. The project has
no external service dependencies.

```powershell
cd solution
python app.py --report
python app.py --serve --port 8000
```

Open `http://127.0.0.1:8000` for the live dashboard. The report is also
written to `reports/incident_report.md` and the machine-readable result to
`reports/incident.json`.

For a month-long bookstore simulation with hourly telemetry, run:

```powershell
python solution/app.py --month --serve --port 8000
```

The dashboard includes daily incident counts, date-based failure analysis,
interactive service topology, and an analyst queue that explains likely root
causes.

To replay a different drop, put replacement files in `sabotage_drops/` using
the same names as the files in `datasets/`, then run:

```powershell
python solution/app.py --data-dir sabotage_drops --report
```
