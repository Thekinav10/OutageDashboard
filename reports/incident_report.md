# Incident Report: Slow Cascade

**Status:** Detected
**Earliest detectable signal:** minute 720.0
**Recommended human intervention:** minute 720.0

## Root cause
The originating service was **network-gateway**, first showing a sustained anomaly at minute 35340.0.
The closest related change was **cfg-month-042** at minute 34560.0: Updated internal routing table for backbone service mesh.

## Propagation timeline
| Minute | From | To | Lag |
|---:|---|---|---:|
| 36540.0 | network-gateway | auth-service | 1200.0 min |
| 35580.0 | network-gateway | session-store | 240.0 min |
| 36540.0 | network-gateway | inventory-service | 1200.0 min |
| 36540.0 | network-gateway | search-service | 1200.0 min |
| 36840.0 | network-gateway | media-upload | 1500.0 min |
| 35520.0 | network-gateway | storefront-service | 180.0 min |
| 36540.0 | network-gateway | catalog-service | 1200.0 min |
| 36720.0 | auth-service | payments-service | 180.0 min |
| 36600.0 | auth-service | profile-service | 60.0 min |
| 36480.0 | auth-service | chat-support | -60.0 min |
| 36600.0 | auth-service | cart-service | 60.0 min |
| 36660.0 | auth-service | wishlist-service | 120.0 min |
| 36480.0 | auth-service | reviews-service | -60.0 min |
| 36600.0 | auth-service | order-history | 60.0 min |
| 36660.0 | auth-service | fraud-service | 120.0 min |
| 36600.0 | auth-service | customer-support | 60.0 min |
| 36840.0 | inventory-service | checkout-service | 300.0 min |
| 36900.0 | inventory-service | order-service | 360.0 min |
| 720.0 | inventory-service | fulfillment-service | -35820.0 min |
| 36720.0 | inventory-service | returns-service | 180.0 min |
| 36600.0 | search-service | recommendation-engine | 60.0 min |
| 39360.0 | search-service | analytics-ingest | 2820.0 min |
| 36480.0 | catalog-service | isbn-service | -60.0 min |
| 36540.0 | catalog-service | pricing-service | 0.0 min |
| 36600.0 | catalog-service | promotions-service | 60.0 min |
| 36600.0 | payments-service | billing-service | -120.0 min |
| 36900.0 | checkout-service | notifications-service | 60.0 min |
| 720.0 | checkout-service | shipping-service | -36120.0 min |

## Why this is actionable
The detector requires a sustained rising latency trend and uses the dependency graph to separate a spreading incident from an isolated noisy spike. It alerts at the first warning-level signal, before hard failure.
