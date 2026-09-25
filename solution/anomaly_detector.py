"""Robust, label-free anomaly detection for noisy service metrics."""

from collections import defaultdict
from statistics import median

try:
    from .config import ANOMALY_SCORE_ALERT, BASELINE_POINTS, EARLY_WARNING_SCORE, MIN_WINDOW
except ImportError:
    from config import ANOMALY_SCORE_ALERT, BASELINE_POINTS, EARLY_WARNING_SCORE, MIN_WINDOW


def _mad(values: list[float], center: float) -> float:
    return median([abs(value - center) for value in values]) or 1.0


def _slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    x_center = (len(values) - 1) / 2
    y_center = sum(values) / len(values)
    denominator = sum((index - x_center) ** 2 for index in range(len(values)))
    return sum((index - x_center) * (value - y_center) for index, value in enumerate(values)) / denominator


def detect_anomalies(metrics: list[dict]) -> list[dict]:
    by_service = defaultdict(list)
    for row in metrics:
        by_service[row["service"]].append(row)

    findings = []
    for service, rows in by_service.items():
        rows.sort(key=lambda row: row["timestamp_min"])
        baseline = rows[:BASELINE_POINTS]
        baseline_latency = median([row["latency_ms"] for row in baseline])
        baseline_error = median([row["error_rate_pct"] for row in baseline]) or 0.01
        latency_scale = _mad([row["latency_ms"] for row in baseline], baseline_latency)
        for index, row in enumerate(rows):
            window = rows[max(0, index - MIN_WINDOW + 1): index + 1]
            latencies = [item["latency_ms"] for item in window]
            current_latency = median(latencies)
            latency_ratio = current_latency / max(baseline_latency, 0.1)
            error_ratio = row["error_rate_pct"] / baseline_error
            robust_deviation = (current_latency - baseline_latency) / latency_scale
            trend = _slope(latencies)
            score = max(0.0, robust_deviation / 4) + max(0.0, latency_ratio - 1) + max(0.0, error_ratio - 1) * 0.15
            level = "critical" if score >= ANOMALY_SCORE_ALERT else "warning" if score >= EARLY_WARNING_SCORE else "normal"
            findings.append({
                **row,
                "baseline_latency_ms": round(baseline_latency, 2),
                "latency_ratio": round(latency_ratio, 2),
                "error_ratio": round(error_ratio, 2),
                "trend_ms_per_sample": round(trend, 2),
                "anomaly_score": round(score, 2),
                "level": level,
            })
    return sorted(findings, key=lambda row: (row["timestamp_min"], row["service"]))


def service_onsets(findings: list[dict], threshold: float = EARLY_WARNING_SCORE) -> dict[str, float]:
    onsets = {}
    for row in findings:
        if row["anomaly_score"] >= threshold and row["service"] not in onsets:
            onsets[row["service"]] = row["timestamp_min"]
    return onsets
