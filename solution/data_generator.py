"""Deterministic month-long telemetry for a realistic replay/demo mode."""

import random
from pathlib import Path

try:
    from .data_loader import load_dependencies
except ImportError:
    from data_loader import load_dependencies


SERVICES = {
    "network-gateway": 42,
    "auth-service": 58,
    "session-store": 36,
    "storefront-service": 54,
    "catalog-service": 82,
    "isbn-service": 61,
    "pricing-service": 74,
    "cart-service": 96,
    "wishlist-service": 68,
    "reviews-service": 91,
    "promotions-service": 63,
    "order-service": 146,
    "order-history": 88,
    "fraud-service": 105,
    "fulfillment-service": 128,
    "returns-service": 116,
    "customer-support": 73,
    "inventory-service": 72,
    "search-service": 88,
    "media-upload": 110,
    "payments-service": 132,
    "profile-service": 76,
    "chat-support": 64,
    "recommendation-engine": 105,
    "checkout-service": 170,
    "billing-service": 118,
    "notifications-service": 96,
    "shipping-service": 112,
    "analytics-ingest": 142,
    "cdn-edge": 29,
    "cache-gateway": 34,
}

BOOKSTORE_DEPENDENCIES = {
    "storefront-service": ["network-gateway", "catalog-service", "pricing-service"],
    "catalog-service": ["network-gateway"],
    "isbn-service": ["catalog-service"],
    "pricing-service": ["catalog-service"],
    "cart-service": ["auth-service", "session-store", "catalog-service", "pricing-service"],
    "wishlist-service": ["auth-service", "catalog-service"],
    "reviews-service": ["auth-service", "catalog-service"],
    "promotions-service": ["catalog-service", "pricing-service"],
    "order-service": ["payments-service", "inventory-service", "fraud-service"],
    "order-history": ["auth-service", "order-service", "session-store"],
    "fraud-service": ["auth-service", "payments-service"],
    "fulfillment-service": ["order-service", "shipping-service", "inventory-service"],
    "returns-service": ["order-service", "inventory-service", "payments-service"],
    "customer-support": ["auth-service", "order-history", "reviews-service"],
}


def _distance_from_root(service: str, dependencies: dict[str, list[str]], memo: dict[str, int]) -> int:
    if service == "network-gateway":
        return 0
    if service in memo:
        return memo[service]
    upstreams = dependencies.get(service, [])
    if not upstreams:
        memo[service] = 99
    else:
        memo[service] = min(_distance_from_root(upstream, dependencies, memo) for upstream in upstreams) + 1
    return memo[service]


def generate_month_dataset(data_dir: Path) -> dict:
    """Create 30 days of hourly metrics while keeping the real dependency map."""
    rng = random.Random(20260925)
    dependencies = {**load_dependencies(data_dir / "dependency_map.json"), **BOOKSTORE_DEPENDENCIES}
    distances = {service: _distance_from_root(service, dependencies, {}) for service in SERVICES}
    rows = []
    hours = 30 * 24
    incident_start = 24 * 24
    for hour in range(hours + 1):
        hour_of_day = hour % 24
        day_of_week = (hour // 24) % 7
        business_load = 1.16 if 8 <= hour_of_day <= 18 else 0.9 if hour_of_day < 6 else 1.02
        weekend_factor = 0.84 if day_of_week >= 5 else 1.0
        daily_cycle = business_load * weekend_factor
        for service, base_latency in SERVICES.items():
            distance = distances[service]
            cascade = max(0, hour - incident_start - distance * 5)
            drift = cascade * (0.55 + distance * 0.16) if distance < 99 else 0
            scheduled_blip = 16 if hour % 168 in (2, 3) and service in {"search-service", "analytics-ingest"} else 0
            latency = max(5, base_latency * daily_cycle + drift + scheduled_blip + rng.gauss(0, base_latency * 0.06))
            volume = max(80, 900 * daily_cycle + rng.gauss(0, 65))
            error_rate = max(0.01, 0.08 + max(0, cascade) * 0.012 + rng.random() * 0.12)
            if service == "network-gateway" and hour >= incident_start:
                error_rate += min(4.5, cascade * 0.018)
            rows.append({
                "timestamp_min": float(hour * 60),
                "service": service,
                "latency_ms": round(latency, 2),
                "request_volume": round(volume, 2),
                "error_rate_pct": round(error_rate, 2),
            })
    changes = [
        {"timestamp_min": float(day * 24 * 60 + 9 * 60), "service": "analytics-ingest", "change_id": f"month-{day:02d}", "description": "Routine scheduled schema and index maintenance"}
        for day in range(1, 30, 3)
    ]
    changes.append({
        "timestamp_min": float(incident_start * 60),
        "service": "network-gateway",
        "change_id": "cfg-month-042",
        "description": "Updated internal routing table for backbone service mesh",
    })
    return {"metrics": rows, "changes": sorted(changes, key=lambda row: row["timestamp_min"]), "dependencies": dependencies, "window": "30 days / hourly samples / bookstore topology"}
