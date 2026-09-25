# Incident Report: Slow Cascade

**Status:** Detected
**Earliest detectable signal:** minute 63.0
**Recommended human intervention:** minute 63.0

## Root cause
The originating service was **network-gateway**, first showing a sustained anomaly at minute 66.0.
The closest related change was **cfg-1003** at minute 42.0: Updated internal routing table for backbone service mesh (v4.7 rollout).

## Propagation timeline
| Minute | From | To | Lag |
|---:|---|---|---:|
| 63.0 | network-gateway | auth-service | -3.0 min |
| 63.0 | network-gateway | session-store | -3.0 min |
| 78.0 | network-gateway | inventory-service | 12.0 min |
| 72.0 | network-gateway | search-service | 6.0 min |
| 78.0 | network-gateway | media-upload | 12.0 min |
| 84.0 | auth-service | payments-service | 21.0 min |
| 81.0 | auth-service | profile-service | 18.0 min |
| 84.0 | auth-service | chat-support | 21.0 min |
| 96.0 | inventory-service | checkout-service | 18.0 min |
| 84.0 | search-service | recommendation-engine | 12.0 min |
| 114.0 | search-service | analytics-ingest | 42.0 min |
| 96.0 | payments-service | billing-service | 12.0 min |
| 111.0 | checkout-service | notifications-service | 15.0 min |
| 117.0 | checkout-service | shipping-service | 21.0 min |

## Why this is actionable
The detector requires a sustained rising latency trend and uses the dependency graph to separate a spreading incident from an isolated noisy spike. It alerts at the first warning-level signal, before hard failure.
