"""CLI entry point for replaying the six-hour outage scenario."""

import argparse
from pathlib import Path

from anomaly_detector import detect_anomalies
from cascade_detector import detect_cascade
from config import DATA_DIR
from dashboard import serve
from data_loader import load_dataset
from incident_report import build_result, write_reports
from trend_detector import detect_trends


def run(data_dir=DATA_DIR) -> dict:
    data_dir = Path(data_dir)
    dataset = load_dataset(data_dir)
    findings = detect_anomalies(dataset["metrics"])
    trends = detect_trends(findings)
    cascade = detect_cascade(findings, dataset["dependencies"], dataset["changes"])
    return build_result(dataset, findings, trends, cascade)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay and diagnose a cascading outage")
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--report", action="store_true", help="write Markdown and JSON reports")
    parser.add_argument("--serve", action="store_true", help="serve the browser dashboard")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    result = run(args.data_dir)
    if args.report or not args.serve:
        paths = write_reports(result)
        print(f"Root cause: {result['cascade'].get('root_cause', {}).get('change_id', 'none')}")
        print(f"Earliest detectable signal: minute {result['earliest_detectable_min']}")
        print(f"Reports: {paths[0]}, {paths[1]}")
    if args.serve:
        serve(result, port=args.port)


if __name__ == "__main__":
    main()
