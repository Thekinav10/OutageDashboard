"""Generate human-readable and JSON incident artifacts."""

import json
from collections import defaultdict
from pathlib import Path

try:
    from .config import REPORT_DIR
    from .root_cause import rank_changes
except ImportError:
    from config import REPORT_DIR
    from root_cause import rank_changes


def build_result(dataset: dict, findings: list[dict], trends: list[dict], cascade: dict) -> dict:
    ranked = rank_changes(dataset["changes"], cascade)
    earliest = min((row["timestamp_min"] for row in findings if row["level"] != "normal"), default=None)
    intervention = min((row["timestamp_min"] for row in findings if row["anomaly_score"] >= 1.45), default=earliest)
    latency_by_minute = defaultdict(list)
    incident_counts = defaultdict(int)
    incidents_by_minute = defaultdict(int)
    daily_incidents = defaultdict(lambda: defaultdict(int))
    observed_services = set()
    for row in findings:
        observed_services.add(row["service"])
        latency_by_minute[row["timestamp_min"]].append(row["latency_ms"])
        if row["level"] != "normal":
            incident_counts[row["service"]] += 1
            incidents_by_minute[row["timestamp_min"]] += 1
            daily_incidents[str(int(row["timestamp_min"] // 1440))][row["service"]] += 1
    latency_series = [
        {"timestamp_min": timestamp, "latency_ms": round(sum(values) / len(values), 2)}
        for timestamp, values in sorted(latency_by_minute.items())
    ]
    incident_points = sorted(incidents_by_minute.items())
    baseline_cutoff = incident_points[0][0] + (incident_points[-1][0] - incident_points[0][0]) * 0.2 if incident_points else 0
    baseline_incidents = [count for timestamp, count in incident_points if timestamp <= baseline_cutoff]
    incident_threshold = max(1, (max(baseline_incidents) + 1) if baseline_incidents else 1)
    return {
        "window": dataset.get("window", "6-hour supplied replay"),
        "sample_count": len(findings),
        "detected": cascade["detected"],
        "earliest_detectable_min": earliest,
        "recommended_intervention_min": intervention,
        "cascade": cascade,
        "dependencies": dataset["dependencies"],
        "ranked_changes": ranked,
        "trend_evidence": trends,
        "latency_series": latency_series,
        "incident_series": [
            {"timestamp_min": timestamp, "incident_count": count}
            for timestamp, count in sorted(incidents_by_minute.items())
        ],
        "incident_daily_series": [
            {"day": day, "incident_count": sum(daily_incidents.get(str(day), {}).values())}
            for day in range(int(max((row["timestamp_min"] for row in findings), default=0) // 1440) + 1)
        ],
        "incident_threshold": incident_threshold,
        "daily_incidents": {
            day: dict(sorted(services.items(), key=lambda item: (-item[1], item[0])))
            for day, services in sorted(daily_incidents.items())
        },
        "calendar_start": dataset.get("calendar_start", "2026-09-01"),
        "incident_counts": dict(sorted(incident_counts.items(), key=lambda item: (-item[1], item[0]))),
        "service_health": {service: incident_counts.get(service, 0) for service in sorted(observed_services)},
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
