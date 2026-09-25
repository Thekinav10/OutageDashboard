# Incident Report: Slow Cascade

**Status:** Detected
**Earliest detectable signal:** minute 3360.0
**Recommended human intervention:** minute 3360.0

## Root cause
The originating service was **network-gateway**, first showing a sustained anomaly at minute 36060.0.
The closest related change was **cfg-month-042** at minute 34560.0: Updated internal routing table for backbone service mesh.

## Propagation timeline
| Minute | From | To | Lag |
|---:|---|---|---:|
| 36120.0 | network-gateway | auth-service | 60.0 min |
| 36120.0 | network-gateway | session-store | 60.0 min |
| 36300.0 | network-gateway | inventory-service | 240.0 min |
| 37620.0 | network-gateway | search-service | 1560.0 min |
| 37560.0 | network-gateway | media-upload | 1500.0 min |
| 37560.0 | auth-service | payments-service | 1440.0 min |
| 37500.0 | auth-service | profile-service | 1380.0 min |
| 36360.0 | auth-service | chat-support | 240.0 min |
| 36780.0 | inventory-service | checkout-service | 480.0 min |
| 36480.0 | search-service | recommendation-engine | -1140.0 min |
| 36540.0 | search-service | analytics-ingest | -1080.0 min |
| 37620.0 | payments-service | billing-service | 60.0 min |
| 37440.0 | checkout-service | notifications-service | 660.0 min |
| 37440.0 | checkout-service | shipping-service | 660.0 min |

## Why this is actionable
The detector requires a sustained rising latency trend and uses the dependency graph to separate a spreading incident from an isolated noisy spike. It alerts at the first warning-level signal, before hard failure.
