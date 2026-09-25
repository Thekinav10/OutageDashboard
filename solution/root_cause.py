"""Rank configuration changes against the first sustained anomaly."""


def rank_changes(changes: list[dict], cascade: dict) -> list[dict]:
    onset = cascade.get("root_onset_min")
    root_service = cascade.get("root_service")
    ranked = []
    for change in changes:
        time_distance = abs(change["timestamp_min"] - onset) if onset is not None else 999
        score = max(0.0, 1.0 - time_distance / 60)
        if change["service"] == root_service:
            score += 1.0
        ranked.append({**change, "causal_score": round(score, 2)})
    return sorted(ranked, key=lambda item: item["causal_score"], reverse=True)
