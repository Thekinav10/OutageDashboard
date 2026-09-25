"""Combine metric onsets and graph topology into a cascade diagnosis."""

from anomaly_detector import service_onsets
from dependency_graph import propagation_path, reverse_graph


def _descendants(service: str, dependencies: dict[str, list[str]]) -> set[str]:
    callers = reverse_graph(dependencies)
    pending = [service]
    seen = set()
    while pending:
        current = pending.pop()
        for dependent in callers.get(current, []):
            if dependent not in seen:
                seen.add(dependent)
                pending.append(dependent)
    return seen


def detect_cascade(findings: list[dict], dependencies: dict[str, list[str]], changes: list[dict]) -> dict:
    onsets = service_onsets(findings)
    if not onsets:
        return {"detected": False, "onsets": {}, "path": [], "root_cause": None}
    changed_services = {change["service"] for change in changes}
    candidates = []
    for service, onset in onsets.items():
        descendants = _descendants(service, dependencies)
        downstream_count = sum(1 for other in descendants if other in onsets and onsets[other] >= onset)
        has_matching_change = service in changed_services
        candidates.append((has_matching_change, downstream_count, -onset, service))
    _, _, _, root = max(candidates)
    path = propagation_path(root, dependencies, onsets)
    related_changes = [change for change in changes if change["timestamp_min"] <= onsets[root] + 30]
    related_changes.sort(key=lambda change: abs(change["timestamp_min"] - onsets[root]))
    change = next((item for item in related_changes if item["service"] == root), related_changes[0] if related_changes else None)
    return {
        "detected": len(path) >= 1 or len(onsets) >= 2,
        "root_service": root,
        "root_onset_min": onsets[root],
        "onsets": onsets,
        "path": path,
        "root_cause": change,
    }
