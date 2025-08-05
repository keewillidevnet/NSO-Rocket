# NSO‑Rocket Configurations

This folder contains JSON configuration files that control the behavior of NSO‑Rocket workflows and agents.

## Files

### `async-settings.json`
Defines how NSO‑Rocket handles **parallel processing** and **API call batching**:
- `batchSize` — Number of devices processed in each cycle
- `concurrentRequests` — How many devices are checked simultaneously
- `timeoutSeconds` — API timeout for each request
- `maxRetries` — How many retry attempts before skipping a device

### `topology-weights.json`
Controls **drift severity scoring** based on device role:
- `core` — High impact (weight 3)
- `distribution` — Medium impact (weight 2)
- `access` — Lower impact (weight 1)
- `lab` — Minimal impact (weight 0.5)
- `default` — Fallback weight (1)

## Notes
- Adjust `async-settings.json` for **performance tuning** (large environments may require smaller batch sizes).
- Adjust `topology-weights.json` to align with your **network architecture**.