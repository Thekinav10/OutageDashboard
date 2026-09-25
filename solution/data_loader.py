"""Load the three input streams into small, testable Python structures."""

import csv
import json
from pathlib import Path


def _number(value: str) -> float:
    return float(value)


def load_metrics(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = []
        for row in csv.DictReader(stream):
            rows.append({
                "timestamp_min": _number(row["timestamp_min"]),
                "service": row["service"],
                "latency_ms": _number(row["latency_ms"]),
                "request_volume": _number(row["request_volume"]),
                "error_rate_pct": _number(row["error_rate_pct"]),
            })
    return rows


def load_changes(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            {**row, "timestamp_min": _number(row["timestamp_min"])}
            for row in csv.DictReader(stream)
        ]


def load_dependencies(path: Path) -> dict[str, list[str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_dataset(data_dir: Path) -> dict:
    return {
        "metrics": load_metrics(data_dir / "metrics_stream.csv"),
        "changes": load_changes(data_dir / "config_changes.csv"),
        "dependencies": load_dependencies(data_dir / "dependency_map.json"),
    }
