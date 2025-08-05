# Compliance Workflows

This folder contains workflows focused on **config compliance and drift detection**.

## Files

### `config-drift-detection.json`
Performs:
- **Async config polling** from NSO and live devices
- **Topology‑aware severity scoring** (weighted from `configs/topology-weights.json`)
- **Slack alerts** for high severity drift
- **Dashboard log output** for visualization in `dashboards/drift-health.json`

## Notes
- Ensure `configs/async-settings.json` and `configs/topology-weights.json` are properly tuned.
- Connect Slack + Grafana before running in production.