# 📊 NSO‑Rocket Dashboards

This folder contains **visualization templates** for NSO‑Rocket workflows.

---

## Files

### `drift-health.json`
A starter Grafana dashboard showing:
- **Drift Percentage Over Time**
- **Top Devices by Drift Severity**
- **Remediation Success Rate**

### `discovery-health.json`
A starter Grafana dashboard showing:
- **Discovered Devices**
- **Device Status and Last Seen Timestamp**

---

## Notes
- Import these JSON files into **Grafana** (or adapt to n8n HTML output) to visualize drift and discovery data.
- Update data source queries as needed to point to your environment.