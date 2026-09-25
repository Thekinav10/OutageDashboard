"""Zero-dependency SOC dashboard for the replay result."""

import html
import json
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer


COLORS = ["#65d6c4", "#f2b56b", "#ff6f61", "#8ba7ff", "#bc8cff", "#70b88a", "#e38fbd", "#c9d3dc"]
CSS = """
:root { --bg:#0b1118; --panel:#111b25; --panel-2:#162330; --border:#273746; --text:#e5edf2; --muted:#8ea0ad; --cyan:#65d6c4; --amber:#f2b56b; --red:#ff6f61; --blue:#8ba7ff; }
* { box-sizing:border-box } body { margin:0; background:var(--bg); color:var(--text); font:13px/1.45 ui-sans-serif,system-ui,sans-serif; letter-spacing:.01em }
.shell { min-height:100vh; display:grid; grid-template-columns:232px 1fr } .rail { background:#0d161f; border-right:1px solid var(--border); padding:22px 16px; display:flex; flex-direction:column; gap:28px }
.brand { display:flex; align-items:center; gap:10px; font-weight:800; letter-spacing:.12em; font-size:13px } .brand-mark { width:30px; height:30px; display:grid; place-items:center; color:#071015; background:var(--cyan); border-radius:6px; font-weight:900 }
.rail-label,.eyebrow { color:var(--muted); font-size:10px; font-weight:800; letter-spacing:.14em; text-transform:uppercase } .nav { display:grid; gap:5px } .nav a { color:#9bacb8; text-decoration:none; padding:11px 10px; border-radius:5px; display:flex; gap:10px; align-items:center } .nav a.active { color:var(--text); background:#1a2a38; border-left:2px solid var(--cyan) } .nav a:hover { background:#162330 }
.rail-footer { margin-top:auto; color:var(--muted); font-size:11px; border-top:1px solid var(--border); padding-top:15px } .dot { width:7px; height:7px; border-radius:50%; background:var(--cyan); display:inline-block; margin-right:6px }
.content { min-width:0; padding:24px 30px 48px; max-width:1600px } .topbar { display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:25px } .topbar h1 { margin:4px 0 0; font-size:26px; letter-spacing:-.02em } .actions { display:flex; gap:10px; align-items:center } .live { color:#b9f0df; border:1px solid #286455; background:#122d2b; border-radius:4px; padding:7px 10px; font-size:11px; font-weight:800; letter-spacing:.1em; text-transform:uppercase } .live i { width:7px; height:7px; border-radius:50%; background:var(--cyan); display:inline-block; margin-right:6px; box-shadow:0 0 0 3px #204b45 }
.btn { border:1px solid var(--border); color:var(--muted); background:var(--panel); border-radius:4px; padding:8px 11px; font:inherit; font-size:11px } .btn:hover { color:var(--text); border-color:#456174 }
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:14px } .kpi,.panel { background:var(--panel); border:1px solid var(--border); border-radius:6px } .kpi { padding:16px 17px; min-height:106px; position:relative; overflow:hidden } .kpi:after { content:""; position:absolute; left:0; bottom:0; height:3px; width:100%; background:var(--cyan) } .kpi.warn:after { background:var(--amber) } .kpi.danger:after { background:var(--red) } .kpi-value { font-size:28px; font-weight:750; margin:10px 0 2px; letter-spacing:-.03em; overflow-wrap:anywhere } .kpi-note { color:var(--muted); font-size:11px }
.panel { padding:18px } .panel-head { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px } .panel h2 { font-size:14px; margin:3px 0 3px; letter-spacing:.01em } .panel-sub { color:var(--muted); font-size:11px } .layout { display:grid; grid-template-columns:minmax(0,1.55fr) minmax(300px,.85fr); gap:14px } .stack { display:grid; gap:14px; align-content:start }
.chart { display:block; width:100%; height:auto; min-height:220px } .chart text { fill:var(--muted); font-size:10px } .grid-line { stroke:#263541; stroke-width:1 } .line { fill:none; stroke:var(--cyan); stroke-width:2.5; stroke-linecap:round; stroke-linejoin:round } .area { fill:#65d6c4; opacity:.08 } .threshold { stroke:var(--red); stroke-width:1.5; stroke-dasharray:5 5 } .marker { stroke:var(--amber); stroke-width:1; stroke-dasharray:2 4 } .end-dot { fill:var(--amber); stroke:#0b1118; stroke-width:3 } .chart-legend { display:flex; gap:18px; color:var(--muted); font-size:11px } .chart-legend span:before { content:""; width:8px; height:8px; display:inline-block; border-radius:2px; background:var(--cyan); margin-right:6px } .chart-legend span:last-child:before { background:var(--amber) }
.plot-point { fill:var(--cyan); opacity:.08; cursor:crosshair } .plot-point:hover { opacity:1; r:5 } .chart-wrap { position:relative } .tooltip { position:absolute; display:none; pointer-events:none; padding:7px 9px; border:1px solid #456174; border-radius:4px; background:#0d161f; color:var(--text); font-size:11px; box-shadow:0 6px 18px #05090d } .range-controls { display:flex; gap:4px; margin-top:4px } .range-controls button { border:1px solid var(--border); border-radius:3px; background:var(--panel-2); color:var(--muted); padding:4px 7px; font:inherit; font-size:10px; cursor:pointer } .range-controls button.active,.range-controls button:hover { color:var(--cyan); border-color:#3b857b }
.pie-layout { display:flex; align-items:center; gap:18px; min-height:220px } .pie { width:162px; height:162px; border-radius:50%; flex:none; border:9px solid #192632; display:grid; place-items:center; position:relative } .pie span { display:grid; place-items:center; width:76px; height:76px; border-radius:50%; background:var(--panel); color:var(--text); font-size:20px; font-weight:800 } .legend { list-style:none; padding:0; margin:0; width:100% } .legend li { display:flex; align-items:center; gap:8px; margin:8px 0; font-size:11px } .legend i { width:8px; height:8px; border-radius:2px; flex:none } .legend span { color:#b8c5cc; flex:1; overflow-wrap:anywhere } .legend strong { color:var(--text) }
.health { display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:7px } .service { background:var(--panel-2); border:1px solid #263a4a; border-radius:4px; padding:9px 10px; display:flex; align-items:center; gap:8px; min-width:0 } .service span { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:#c1ced5; font-size:11px } .service b { color:var(--muted); font-size:10px; margin-left:auto } .service i { width:7px; height:7px; border-radius:50%; background:var(--cyan); flex:none } .service.alert i { background:var(--red); box-shadow:0 0 0 3px #4b272c } .service.alert { border-color:#56333a }
.graph-shell { overflow:auto; min-height:500px; background:#0b141d; border:1px solid #203442; border-radius:5px; padding:10px } .relation-graph { display:block; min-width:1120px; width:100%; height:auto; touch-action:none } .graph-edge { stroke:#365265; stroke-width:1.2; opacity:.78; marker-end:url(#arrow) } .graph-edge.impacted { stroke:var(--red); stroke-width:2; opacity:.95 } .graph-edge.related,.graph-edge.selected { stroke:#6ee7b7; stroke-width:2.5; opacity:1 } .graph-edge.daily-highlight { stroke:#f2a65a; stroke-width:3; opacity:1 } .graph-edge.daily-muted { opacity:.12 } .graph-node { cursor:grab } .graph-node:active { cursor:grabbing } .graph-node rect { fill:#172735; stroke:#385266; stroke-width:1 } .graph-node text { fill:#cbd7dd; font-size:11px; font-family:inherit; pointer-events:none } .graph-node .node-meta { fill:var(--muted); font-size:9px } .graph-node.impacted rect { fill:#2a1d25; stroke:#9a4a50 } .graph-node.root rect { fill:#332b1d; stroke:var(--amber); stroke-width:2 } .graph-node.healthy rect { fill:#13242a; stroke:#2f5961 } .graph-node.related rect,.graph-node.selected rect { fill:#14352e; stroke:#6ee7b7; stroke-width:2 } .graph-node.daily-highlight rect { fill:#4a2b18; stroke:#f2a65a; stroke-width:2.5 } .graph-node.daily-muted { opacity:.22 } .graph-legend { display:flex; gap:16px; align-items:center; color:var(--muted); font-size:10px; padding:8px 4px 2px } .graph-legend i { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:5px; background:var(--cyan) } .graph-legend i.root { background:var(--amber) } .graph-legend i.impacted { background:var(--red) } .graph-legend i.selected { background:#6ee7b7 } .graph-legend i.daily { background:#f2a65a } .graph-legend i.edge { width:18px; height:2px; border-radius:0; background:#365265; vertical-align:middle }
.day-control { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:10px; letter-spacing:.08em; text-transform:uppercase } .day-control input { color:var(--text); background:var(--panel-2); border:1px solid #456174; border-radius:4px; padding:7px 8px; font:inherit; color-scheme:dark } .daily-cause { margin:8px 0 0; padding:9px 11px; border-left:3px solid #f2a65a; background:#2a2119; color:#ffd09c; font-size:11px; border-radius:3px }
.queue { width:100%; border-collapse:collapse } .queue th { color:var(--muted); font-size:10px; text-align:left; letter-spacing:.1em; text-transform:uppercase; padding:9px 8px; border-bottom:1px solid var(--border) } .queue td { padding:11px 8px; border-bottom:1px solid #1d2b37; color:#c2cdd4; font-size:11px } .queue tr:last-child td { border-bottom:0 } .severity { font-size:10px; font-weight:800; letter-spacing:.08em; padding:4px 6px; border-radius:3px; background:#4a252c; color:#ffaaa2 } .severity.watch { color:#ffd194; background:#493822 } .score { color:var(--cyan); font-weight:800 }
.timeline { display:flex; align-items:stretch; overflow:auto; padding:10px 0 14px } .hop { min-width:160px; flex:1; background:var(--panel-2); border:1px solid #30495c; border-radius:5px; padding:12px; position:relative; margin-right:24px } .hop:not(:last-child):after { content:"->"; position:absolute; right:-22px; top:34px; color:var(--amber); font-weight:800 } .hop-time { color:var(--amber); font-size:10px; font-weight:800 } .hop-service { color:#d9e2e6; margin-top:6px; font-size:11px; overflow-wrap:anywhere } .hop-lag { color:var(--muted); font-size:10px; margin-top:5px }
.callout { border-left:3px solid var(--red); background:#1b2029; padding:14px 16px; margin-top:14px; border-radius:4px } .callout strong { color:#ffaaa2 } .muted { color:var(--muted) }
@media(max-width:1000px) { .shell { grid-template-columns:72px 1fr } .rail { padding:20px 10px } .brand strong,.rail-label,.nav a span,.rail-footer { display:none } .brand { justify-content:center } .nav a { justify-content:center } .content { padding:20px } .kpis { grid-template-columns:repeat(2,1fr) } .layout { grid-template-columns:1fr } }
@media(max-width:650px) { .shell { display:block } .rail { height:62px; padding:12px 15px; flex-direction:row; align-items:center; border-right:0; border-bottom:1px solid var(--border) } .brand strong { display:block } .nav { display:flex; margin-left:auto } .nav a { padding:8px; font-size:0 } .nav a span { display:none } .rail-footer { display:none } .content { padding:16px 12px 34px } .topbar { align-items:flex-start; flex-direction:column } .actions { width:100%; justify-content:space-between } .kpis { grid-template-columns:1fr 1fr; gap:8px } .kpi { min-height:92px; padding:12px } .kpi-value { font-size:22px } .pie-layout { align-items:flex-start; flex-direction:column } .pie { width:130px; height:130px } }
"""


def _safe(value: object) -> str:
    return html.escape(str(value))


def _incident_chart(series: list[dict], calendar_start: str) -> str:
    if not series:
        return "<p class='muted'>No telemetry available.</p>"
    values = [item["incident_count"] for item in series]
    low, high = 0, max(values)
    spread = max(high, 1)
    points = []
    markers = []
    for index, item in enumerate(series):
        x = 42 + index / max(len(series) - 1, 1) * 700
        y = 182 - item["incident_count"] / spread * 160
        points.append(f"{x:.1f},{y:.1f}")
        day_date = (date.fromisoformat(calendar_start) + timedelta(days=item["day"])).isoformat()
        markers.append(f"<circle class='plot-point' cx='{x:.1f}' cy='{y:.1f}' r='4' data-time='{item['day'] * 1440}' data-date='{day_date}' data-count='{item['incident_count']}'/>")
    end = points[-1].split(",")
    area = f"42,182 {' '.join(points)} 742,182"
    midpoint = high / 2
    return f"<div class='chart-wrap'><div class='tooltip' id='latency-tooltip'></div><svg class='chart' id='incident-chart' viewBox='0 0 760 210' role='img' aria-label='Interactive daily incident count graph'><line class='grid-line' x1='42' y1='22' x2='742' y2='22'/><line class='grid-line' x1='42' y1='102' x2='742' y2='102'/><line class='grid-line' x1='42' y1='182' x2='742' y2='182'/><text class='scale-max' x='5' y='26'>{high:.0f}</text><text class='scale-mid' x='5' y='106'>{midpoint:.0f}</text><text x='15' y='186'>0</text><polygon class='area' id='incident-area' points='{area}'/><polyline class='line' id='incident-line' points='{' '.join(points)}'/>{''.join(markers)}<circle class='end-dot' cx='{end[0]}' cy='{end[1]}' r='5'/><text x='42' y='204'>first day</text><text x='680' y='204'>last day</text></svg></div>"


def _pie_chart(counts: dict[str, int]) -> tuple[str, str]:
    items = list(counts.items())[:7]
    total = sum(counts.values()) or 1
    angle = 0
    stops, legend = [], []
    for index, (service, count) in enumerate(items):
        end = angle + count / total * 360
        color = COLORS[index % len(COLORS)]
        stops.append(f"{color} {angle:.1f}deg {end:.1f}deg")
        legend.append(f"<li><i style='background:{color}'></i><span>{_safe(service)}</span><strong>{count}</strong></li>")
        angle = end
    pie = f"<div class='pie' style='background:conic-gradient({', '.join(stops)})' role='img' aria-label='Incident distribution'><span>{total}</span></div>"
    return pie, f"<ul class='legend'>{''.join(legend)}</ul>"


def _health_matrix(health: dict[str, int], window: str) -> str:
    services = []
    for service, count in health.items():
        state = " alert" if count else ""
        services.append(f"<div class='service{state}'><i></i><span title='{_safe(service)}: {count} anomaly observations in {_safe(window)}'>{_safe(service)}</span><b>{count} alerts</b></div>")
    return "".join(services) or "<span class='muted'>No service telemetry.</span>"


def _dependency_graph(dependencies: dict[str, list[str]], cascade: dict, failed_only: bool = False) -> str:
    graph_label = "Failed service blast radius" if failed_only else "Microservice dependency graph"
    graph_id = "failed-graph" if failed_only else "topology-graph"
    services = set(dependencies)
    for upstreams in dependencies.values():
        services.update(upstreams)
    impacted = set(cascade.get("onsets", {}))
    if failed_only:
        services = impacted or {cascade.get("root_service", "unknown")}
    memo = {}

    def level(service: str, visiting: set[str] | None = None) -> int:
        if service in memo:
            return memo[service]
        visiting = visiting or set()
        if service in visiting or not dependencies.get(service):
            memo[service] = 0
            return 0
        visiting.add(service)
        memo[service] = max(level(upstream, visiting) for upstream in dependencies[service]) + 1
        visiting.remove(service)
        return memo[service]

    columns = {}
    for service in sorted(services):
        columns.setdefault(level(service), []).append(service)
    column_width, node_width, node_height, row_gap = 260, 210, 44, 28
    graph_height = max(len(items) for items in columns.values()) * (node_height + row_gap) + 60
    positions = {}
    for column, items in columns.items():
        offset = (graph_height - len(items) * (node_height + row_gap)) / 2
        for index, service in enumerate(items):
            positions[service] = (column * column_width + 24, offset + index * (node_height + row_gap))
    edges = []
    for service, upstreams in dependencies.items():
        if service not in services:
            continue
        x2, y2 = positions[service]
        for upstream in upstreams:
            if upstream not in positions or (failed_only and upstream not in impacted):
                continue
            x1, y1 = positions[upstream]
            state = " impacted" if service in impacted and upstream in impacted else ""
            edges.append(f"<line class='graph-edge{state}' style='marker-end:url(#arrow-{graph_id})' data-from='{_safe(upstream)}' data-to='{_safe(service)}' x1='{x1 + node_width}' y1='{y1 + node_height / 2}' x2='{x2}' y2='{y2 + node_height / 2}'/>")
    nodes = []
    root = cascade.get("root_service")
    root_change = cascade.get("root_cause") or {}
    for service, (x, y) in positions.items():
        state = "root" if service == root else "impacted" if service in impacted else "healthy"
        label = "ROOT" if service == root else "IMPACTED" if service in impacted else "NOMINAL"
        reason = f"config {root_change.get('change_id', 'change')}" if service == root else "downstream dependency" if service in impacted else "no active failure"
        nodes.append(f"<g class='graph-node {state}' data-service='{_safe(service)}' data-x='{x}' data-y='{y}' data-start-x='{x}' data-start-y='{y}' transform='translate({x} {y})'><title>{_safe(service)} - {label}: {reason}</title><rect x='0' y='0' width='{node_width}' height='{node_height}' rx='5'/><text x='12' y='19'>{_safe(service)}</text><text class='node-meta' x='12' y='35'>{label} / {_safe(reason)}</text></g>")
    width = max(columns) * column_width + node_width + 28
    interactive = "true"
    return f"<div class='graph-shell'><svg class='relation-graph' data-interactive='{interactive}' id='{graph_id}' viewBox='0 0 {width} {graph_height}' role='img' aria-label='{graph_label}'><defs><marker id='arrow-{graph_id}' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='5' markerHeight='5' orient='auto-start-reverse'><path d='M 0 0 L 10 5 L 0 10 z' fill='#365265'/></marker></defs>{''.join(edges)}{''.join(nodes)}</svg><div class='graph-legend'><span><i class='root'></i>Root signal</span><span><i class='impacted'></i>Failed / impacted</span><span><i class='selected'></i>Selected relation</span><span><i class='edge'></i>Dependency direction</span></div></div>"


def _queue(changes: list[dict]) -> str:
    rows = []
    for index, change in enumerate(changes):
        severity = "CRITICAL" if index == 0 else "WATCH"
        style = "" if index == 0 else " watch"
        day_index = int(float(change.get("timestamp_min", 0)) // 1440)
        rows.append(f"<tr data-day='{day_index}'><td><span class='severity{style}'>{severity}</span></td><td>{_safe(change.get('service'))}</td><td>{_safe(change.get('change_id'))}</td><td>{_safe(change.get('description'))}</td><td class='score'>{change.get('causal_score', 0):.2f}</td></tr>")
    return "".join(rows) or "<tr><td colspan='5' class='muted'>No active detections.</td></tr>"


def _inferred_queue(daily_incidents: dict[str, dict[str, int]], changes: list[dict]) -> str:
    change_days = {int(float(change.get("timestamp_min", 0)) // 1440) for change in changes}
    rows = []
    for day, services in daily_incidents.items():
        if int(day) in change_days:
            continue
        for service, count in list(services.items())[:3]:
            score = min(0.85, 0.25 + count / 30)
            reason = "No config change logged; inferred downstream dependency degradation from telemetry"
            rows.append(f"<tr data-day='{day}'><td><span class='severity watch'>INFERRED</span></td><td>{_safe(service)}</td><td>telemetry-day-{day}</td><td>{reason}</td><td class='score'>{score:.2f}</td></tr>")
    return "".join(rows)


def _timeline(path: list[dict]) -> str:
    return "".join(f"<div class='hop'><div class='hop-time'>MIN {edge['timestamp_min']}</div><div class='hop-service'>{_safe(edge['from'])} -> {_safe(edge['to'])}</div><div class='hop-lag'>+{edge['lag_min']} min propagation</div></div>" for edge in path) or "<span class='muted'>No propagation path recorded.</span>"


def render_dashboard(result: dict) -> str:
    cascade = result.get("cascade", {})
    counts = result.get("incident_counts", {})
    health = result.get("service_health", counts)
    top_service, top_count = next(iter(counts.items()), ("none", 0))
    total_incidents = sum(counts.values())
    affected = sum(1 for count in health.values() if count)
    mean_latency = sum(item["latency_ms"] for item in result.get("latency_series", [])) / max(len(result.get("latency_series", [])), 1)
    pie, legend = _pie_chart(counts)
    window = _safe(result.get("window", "Replay"))
    root = _safe(cascade.get("root_service", "unknown"))
    change = cascade.get("root_cause") or {}
    timeline = _timeline(cascade.get("path", []))
    relation_tree = _dependency_graph(result.get("dependencies", {}), cascade)
    failed_graph = _dependency_graph(result.get("dependencies", {}), cascade, failed_only=True)
    calendar_start = result.get("calendar_start", "2026-09-01")
    calendar_end = (date.fromisoformat(calendar_start) + timedelta(days=30)).isoformat()
    calendar_days = result.get("daily_incidents", {})
    default_day = max((int(day) for day in calendar_days), default=0)
    selected_date = (date.fromisoformat(calendar_start) + timedelta(days=default_day)).isoformat()
    daily_json = json.dumps(calendar_days)
    dependency_json = json.dumps(result.get("dependencies", {}))
    queue_rows = _queue(result.get("ranked_changes", [])) + _inferred_queue(calendar_days, result.get("ranked_changes", []))
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Sentinel SOC | Platform Defense</title><style>{CSS}</style></head><body><div class='shell'>
<aside class='rail'><div class='brand'><div class='brand-mark'>S</div><strong>SENTINEL SOC</strong></div><div><div class='rail-label'>Workspace</div><nav class='nav'><a class='active' href='#overview'><b>01</b><span>Overview</span></a><a href='#signals'><b>02</b><span>Signals</span></a><a href='#services'><b>03</b><span>Services</span></a><a href='#timeline'><b>04</b><span>Timeline</span></a></nav></div><div class='rail-footer'><span class='dot'></span>Telemetry pipeline<br><span class='muted'>All collectors online</span></div></aside>
<main class='content' id='overview'><header class='topbar'><div><div class='eyebrow'>Security operations / platform integrity</div><h1>Incident command center</h1></div><div class='actions'><span class='live'><i></i>Live replay</span><button class='btn'>{window}</button><button class='btn'>UTC</button></div></header>
<section class='kpis'><article class='kpi danger'><div class='eyebrow'>Active cascade</div><div class='kpi-value'>{'OPEN' if cascade.get('detected') else 'CLEAR'}</div><div class='kpi-note'>Root: {root}</div></article><article class='kpi warn'><div class='eyebrow'>Incident observations</div><div class='kpi-value'>{total_incidents:,}</div><div class='kpi-note'>{affected} affected services</div></article><article class='kpi'><div class='eyebrow'>Mean latency</div><div class='kpi-value'>{mean_latency:.0f}<span class='muted'> ms</span></div><div class='kpi-note'>Across current telemetry window</div></article><article class='kpi'><div class='eyebrow'>Top signal source</div><div class='kpi-value'>{_safe(top_service)}</div><div class='kpi-note'>{top_count} anomaly observations</div></article></section>
<section class='layout' id='signals'><article class='panel'><div class='panel-head'><div><div class='eyebrow'>Daily telemetry</div><h2>Incidents by day</h2><div class='panel-sub'>Hover a point to see the exact date and total incidents recorded that day</div></div><div class='chart-legend'><span>daily incidents</span><span>current day</span></div></div>{_incident_chart(result.get('incident_daily_series', []), result.get('calendar_start', '2026-09-01'))}<div class='range-controls'><button class='active' data-hours='720'>30D</button><button data-hours='168'>7D</button><button data-hours='24'>24H</button><span class='muted' id='range-label'>Full replay window</span></div></article><article class='panel'><div class='panel-head'><div><div class='eyebrow'>Signal attribution</div><h2>Risk mix</h2><div class='panel-sub'>Total anomaly observations by service</div></div></div><div class='pie-layout'>{pie}{legend}</div></article></section>
<section class='panel' id='services' style='margin-top:14px'><div class='panel-head'><div><div class='eyebrow'>Asset inventory</div><h2>Bookstore service posture</h2><div class='panel-sub'>Each number is anomaly observations / replay window. It is not a service count; 0 alerts means no anomaly observations.</div></div><span class='muted'>{len(health)} services monitored / {_safe(window)}</span></div><div class='health'>{_health_matrix(health, window)}</div></section>
<section class='panel' style='margin-top:14px'><div class='panel-head'><div><div class='eyebrow'>Topology map</div><h2>Microservice dependency graph</h2><div class='panel-sub'>Directed service topology and blast radius. Red nodes are impacted; amber is the root signal.</div></div><span class='muted'>{len(result.get('dependencies', {}))} services mapped</span></div>{relation_tree}</section>
<section class='panel' style='margin-top:14px'><div class='panel-head'><div><div class='eyebrow'>Failure analysis</div><h2>Failed service blast radius</h2><div class='panel-sub'>Choose a calendar day to isolate that day's highest-incident service and downstream failures.</div></div><div class='day-control'><label for='incident-day'>Calendar day</label><input id='incident-day' type='date' min='{calendar_start}' max='{calendar_end}' value='{selected_date}'></div></div><div class='daily-cause' id='daily-cause'>Loading daily failure cause...</div>{failed_graph}</section>
<section class='panel' style='margin-top:14px'><div class='panel-head'><div><div class='eyebrow'>Analyst queue</div><h2>Prioritized detection queue</h2><div class='panel-sub'>Purpose: find the configuration change most likely to explain this day's failures. If no change was logged, inferred telemetry reasons are shown for investigation.</div></div><span class='severity' id='queue-day-label'>ALL EVENTS</span></div><div style='overflow:auto'><table class='queue'><thead><tr><th>Action</th><th>Service</th><th>Change ID</th><th>What changed</th><th>Causal score</th></tr></thead><tbody id='queue-body'>{queue_rows}</tbody></table></div></section>
<section class='panel' id='timeline' style='margin-top:14px'><div class='panel-head'><div><div class='eyebrow'>Case graph</div><h2>Dependency propagation</h2><div class='panel-sub'>Directional flow from originating signal to affected services</div></div><span class='muted'>First signal: min {result.get('earliest_detectable_min')}</span></div><div class='timeline'>{timeline}</div><div class='callout'><strong>Likely root change: {_safe(change.get('change_id', 'unknown'))}</strong><br><span class='muted'>{_safe(change.get('description', 'No root change identified.'))}</span></div></section>
</main><script>
const points = document.querySelectorAll('.plot-point');
const tooltip = document.getElementById('latency-tooltip');
const incidentChart = document.getElementById('incident-chart');
const incidentLine = document.getElementById('incident-line');
const incidentArea = document.getElementById('incident-area');
const scaleMax = document.querySelector('.scale-max');
const scaleMid = document.querySelector('.scale-mid');
const endDot = document.querySelector('.end-dot');
points.forEach(point => {{
    point.addEventListener('mouseenter', event => {{
        tooltip.textContent = `${{point.dataset.date}} | ${{point.dataset.count}} incidents`;
        tooltip.style.display = 'block';
        tooltip.style.left = `${{event.offsetX + 12}}px`;
        tooltip.style.top = `${{event.offsetY - 34}}px`;
    }});
    point.addEventListener('mouseleave', () => tooltip.style.display = 'none');
}});
document.querySelectorAll('.range-controls button').forEach(button => button.addEventListener('click', () => {{
    document.querySelectorAll('.range-controls button').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    const hours = Number(button.dataset.hours);
    const times = [...points].map(point => Number(point.dataset.time));
    const cutoff = Math.max(...times) - hours * 60;
    const visible = [...points].filter(point => Number(point.dataset.time) >= cutoff);
    const maxCount = Math.max(...visible.map(point => Number(point.dataset.count)), 1);
    const scaledPoints = visible.map((point, index) => {{
        const x = 42 + index / Math.max(visible.length - 1, 1) * 700;
        const y = 182 - Number(point.dataset.count) / maxCount * 160;
        point.setAttribute('cx', x.toFixed(1));
        point.setAttribute('cy', y.toFixed(1));
        point.style.display = '';
        return `${{x.toFixed(1)}},${{y.toFixed(1)}}`;
    }});
    points.forEach(point => {{ if (!visible.includes(point)) point.style.display = 'none'; }});
    incidentLine.setAttribute('points', scaledPoints.join(' '));
    incidentArea.setAttribute('points', `42,182 ${{scaledPoints.join(' ')}} 742,182`);
    if (scaledPoints.length) {{
        const current = scaledPoints[scaledPoints.length - 1].split(',');
        endDot.setAttribute('cx', current[0]);
        endDot.setAttribute('cy', current[1]);
    }}
    scaleMax.textContent = maxCount;
    scaleMid.textContent = Math.round(maxCount / 2);
    incidentChart.setAttribute('data-range-hours', hours);
    document.getElementById('range-label').textContent = hours === 24 ? 'Last 24 hours' : hours === 168 ? 'Last 7 days' : 'Full replay window';
}}));
const topology = document.querySelector('#topology-graph');
const topologyNodes = [...topology.querySelectorAll('.graph-node')];
const topologyEdges = [...topology.querySelectorAll('.graph-edge')];
const nodesByName = new Map(topologyNodes.map(node => [node.dataset.service, node]));
const nodeWidth = 210;
const nodeHeight = 44;
let dragging = null;
function refreshEdges() {{
    topologyEdges.forEach(edge => {{
        const from = nodesByName.get(edge.dataset.from);
        const to = nodesByName.get(edge.dataset.to);
        if (!from || !to) return;
        const fromX = Number(from.dataset.x);
        const fromY = Number(from.dataset.y);
        const toX = Number(to.dataset.x);
        const toY = Number(to.dataset.y);
        edge.setAttribute('x1', fromX + nodeWidth);
        edge.setAttribute('y1', fromY + nodeHeight / 2);
        edge.setAttribute('x2', toX);
        edge.setAttribute('y2', toY + nodeHeight / 2);
    }});
}}
function highlightNode(selected, graph, graphNodes, graphEdges, nodesByName) {{
    graphNodes.forEach(node => node.classList.remove('selected', 'related'));
    graphEdges.forEach(edge => edge.classList.remove('selected'));
    selected.classList.add('selected');
    const service = selected.dataset.service;
    graphEdges.forEach(edge => {{
        if (edge.dataset.from === service || edge.dataset.to === service) {{
            edge.classList.add('selected');
            const related = nodesByName.get(edge.dataset.from === service ? edge.dataset.to : edge.dataset.from);
            if (related) related.classList.add('related');
        }}
    }});
}}
function bindSelection(graph) {{
    const graphNodes = [...graph.querySelectorAll('.graph-node')];
    const graphEdges = [...graph.querySelectorAll('.graph-edge')];
    const nodesByName = new Map(graphNodes.map(node => [node.dataset.service, node]));
    graphNodes.forEach(node => node.addEventListener('click', () => highlightNode(node, graph, graphNodes, graphEdges, nodesByName)));
}}
bindSelection(topology);
bindSelection(document.querySelector('#failed-graph'));
const dailyIncidents = {daily_json};
const graphDependencies = {dependency_json};
const failedGraph = document.querySelector('#failed-graph');
const incidentDay = document.getElementById('incident-day');
const dailyCause = document.getElementById('daily-cause');
function dailyDownstream(leader) {{
    const affected = new Set([leader]);
    let changed = true;
    while (changed) {{
        changed = false;
        Object.entries(graphDependencies).forEach(([service, upstreams]) => {{
            if (!affected.has(service) && upstreams.some(upstream => affected.has(upstream))) {{
                affected.add(service);
                changed = true;
            }}
        }});
    }}
    return affected;
}}
function updateDailyFailureView() {{
    const start = new Date('{calendar_start}T00:00:00');
    const chosen = new Date(`${{incidentDay.value}}T00:00:00`);
    const dayIndex = Math.round((chosen - start) / 86400000);
    const dayCounts = dailyIncidents[String(dayIndex)] || {{}};
    const leaders = Object.entries(dayCounts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    const leader = leaders.length ? leaders[0][0] : null;
    const affected = leader ? dailyDownstream(leader) : new Set();
    const failedNodes = [...failedGraph.querySelectorAll('.graph-node')];
    const failedEdges = [...failedGraph.querySelectorAll('.graph-edge')];
    failedNodes.forEach(node => {{
        node.classList.remove('daily-highlight', 'daily-muted');
        if (leader && affected.has(node.dataset.service)) node.classList.add('daily-highlight');
        else if (leader) node.classList.add('daily-muted');
    }});
    failedEdges.forEach(edge => {{
        edge.classList.remove('daily-highlight', 'daily-muted');
        if (leader && affected.has(edge.dataset.from) && affected.has(edge.dataset.to)) edge.classList.add('daily-highlight');
        else if (leader) edge.classList.add('daily-muted');
    }});
    const queueRows = [...document.querySelectorAll('#queue-body tr[data-day]')];
    const visibleChanges = queueRows.filter(row => Number(row.dataset.day) === dayIndex);
    queueRows.forEach(row => row.style.display = Number(row.dataset.day) === dayIndex ? '' : 'none');
    document.getElementById('queue-day-label').textContent = visibleChanges.length ? `${{visibleChanges.length}} ${{visibleChanges.length === 1 ? 'CHANGE' : 'CHANGES'}} ON DAY` : 'NO CHANGES';
    dailyCause.textContent = leader ? `Cause candidate: ${{leader}} (${{leaders[0][1]}} incidents). Reason: highest incident source for this day; orange services are downstream propagation symptoms.` : `No failed service incidents recorded for ${{incidentDay.value}}.`;
}}
incidentDay.addEventListener('change', updateDailyFailureView);
updateDailyFailureView();
topologyNodes.forEach(node => node.addEventListener('pointerdown', event => {{
    event.preventDefault();
    node.setPointerCapture(event.pointerId);
    const point = topology.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(topology.getScreenCTM().inverse());
    dragging = {{ node, offsetX: local.x - Number(node.dataset.x), offsetY: local.y - Number(node.dataset.y) }};
}}));
topologyNodes.forEach(node => node.addEventListener('pointermove', event => {{
    if (!dragging || dragging.node !== node) return;
    const point = topology.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(topology.getScreenCTM().inverse());
    const x = Math.max(0, local.x - dragging.offsetX);
    const y = Math.max(0, local.y - dragging.offsetY);
    node.dataset.x = x;
    node.dataset.y = y;
    node.setAttribute('transform', `translate(${{x}} ${{y}})`);
    refreshEdges();
}}));
topologyNodes.forEach(node => node.addEventListener('pointerup', () => {{ dragging = null; }}));
topologyNodes.forEach(node => node.addEventListener('dblclick', () => {{
    node.dataset.x = node.dataset.startX;
    node.dataset.y = node.dataset.startY;
    node.setAttribute('transform', `translate(${{node.dataset.x}} ${{node.dataset.y}})`);
    refreshEdges();
}}));
</script></div></body></html>"""


def serve(result: dict, host: str = "127.0.0.1", port: int = 8000) -> None:
    page = render_dashboard(result).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in {"/api/incident", "/api/live"}:
                payload = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, *_args):
            return

    print(f"Dashboard: http://{host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()
