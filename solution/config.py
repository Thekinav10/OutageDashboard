"""Configuration and paths for the outage detector."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "datasets"
REPORT_DIR = ROOT / "reports"

BASELINE_POINTS = 12
MIN_WINDOW = 5
LATENCY_RATIO_ALERT = 1.45
ERROR_RATIO_ALERT = 2.5
TREND_SLOPE_ALERT = 0.35
ANOMALY_SCORE_ALERT = 2.0
EARLY_WARNING_SCORE = 1.45
