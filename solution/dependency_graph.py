"""Graph helpers. The input maps each service to the services it calls."""

from collections import defaultdict, deque


def reverse_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    callers = defaultdict(list)
    for service, upstreams in dependencies.items():
        for upstream in upstreams:
            callers[upstream].append(service)
    return dict(callers)


def propagation_path(root: str, dependencies: dict[str, list[str]], onsets: dict[str, float]) -> list[dict]:
    callers = reverse_graph(dependencies)
    queue = deque([root])
    visited = {root}
    path = []
    while queue:
        service = queue.popleft()
        for dependent in callers.get(service, []):
            if dependent in visited:
                continue
            visited.add(dependent)
            queue.append(dependent)
            if dependent in onsets:
                path.append({
                    "from": service,
                    "to": dependent,
                    "timestamp_min": onsets[dependent],
                    "lag_min": round(onsets[dependent] - onsets.get(service, onsets[dependent]), 1),
                })
    return path


def reachable_services(root: str, dependencies: dict[str, list[str]]) -> set[str]:
    return {root} | {edge["to"] for edge in propagation_path(root, dependencies, {})}
