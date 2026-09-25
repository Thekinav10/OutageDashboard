"""Find sustained deterioration rather than isolated noisy spikes."""

from collections import defaultdict

from config import MIN_WINDOW, TREND_SLOPE_ALERT


def detect_trends(findings: list[dict]) -> list[dict]:
    by_service = defaultdict(list)
    for row in findings:
        by_service[row["service"]].append(row)
    results = []
    for service, rows in by_service.items():
        rows.sort(key=lambda row: row["timestamp_min"])
        for index in range(MIN_WINDOW - 1, len(rows)):
            window = rows[index - MIN_WINDOW + 1:index + 1]
            rising = sum(item["trend_ms_per_sample"] > TREND_SLOPE_ALERT for item in window)
            if rising >= MIN_WINDOW - 1 and window[-1]["latency_ratio"] >= 1.25:
                results.append({
                    "service": service,
                    "timestamp_min": window[-1]["timestamp_min"],
                    "slope_ms_per_sample": window[-1]["trend_ms_per_sample"],
                    "confidence": round(min(0.99, 0.5 + rising / MIN_WINDOW * 0.1 + window[-1]["latency_ratio"] / 10), 2),
                })
                break
    return sorted(results, key=lambda row: row["timestamp_min"])
