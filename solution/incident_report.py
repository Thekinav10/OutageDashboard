"""Generate human-readable and JSON incident artifacts."""

import json
from pathlib import Path

from config import REPORT_DIR
from root_cause import rank_changes


def build_result(dataset: dict, findings: list[dict], trends: list[dict], cascade: dict) -> dict:
    ranked = rank_changes(dataset["changes"], cascade)
    earliest = min((row["timestamp_min"] for row in findings if row["level"] != "normal"), default=None)
    intervention = min((row["timestamp_min"] for row in findings if row["anomaly_score"] >= 1.45), default=earliest)
    return {
        "detected": cascade["detected"],
        "earliest_detectable_min": earliest,
        "recommended_intervention_min": intervention,
        "cascade": cascade,
        "ranked_changes": ranked,
        "trend_evidence": trends,
    }


def render_markdown(result: dict) -> str:
    cascade = result["cascade"]
    change = cascade.get("root_cause") or {}
    lines = [
        "# Incident Report: Slow Cascade",
        "",
        f"**Status:** {'Detected' if result['detected'] else 'No cascade detected'}",
        f"**Earliest detectable signal:** minute {result['earliest_detectable_min']}",
        f"**Recommended human intervention:** minute {result['recommended_intervention_min']}",
        "",
        "## Root cause",
        f"The originating service was **{cascade.get('root_service', 'unknown')}**, first showing a sustained anomaly at minute {cascade.get('root_onset_min', 'unknown')}.",
        f"The closest related change was **{change.get('change_id', 'unknown')}** at minute {change.get('timestamp_min', 'unknown')}: {change.get('description', 'unknown')}.",
        "",
        "## Propagation timeline",
        "| Minute | From | To | Lag |",
        "|---:|---|---|---:|",
    ]
    lines.extend(f"| {edge['timestamp_min']} | {edge['from']} | {edge['to']} | {edge['lag_min']} min |" for edge in cascade.get("path", []))
    lines.extend(["", "## Why this is actionable", "The detector requires a sustained rising latency trend and uses the dependency graph to separate a spreading incident from an isolated noisy spike. It alerts at the first warning-level signal, before hard failure."])
    return "\n".join(lines) + "\n"


def write_reports(result: dict, report_dir: Path = REPORT_DIR) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = report_dir / "incident_report.md"
    json_path = report_dir / "incident.json"
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return markdown_path, json_path
