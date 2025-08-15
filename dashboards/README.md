# 📊 NSO-Rocket Dashboards

This folder contains **visualization templates** and **runtime telemetry** for NSO-Rocket workflows.

---

## Files (Static Dashboard Definitions)

### `drift-health.json`
A starter Grafana dashboard showing:
- **Drift Percentage Over Time**
- **Top Devices by Drift Severity**
- **Remediation Success Rate**

### `discovery-health.json`
A starter Grafana dashboard showing:
- **Discovered Devices**
- **Device Status and Last Seen Timestamp**

> Import these JSON files into **Grafana** (or adapt to n8n HTML output) to visualize drift and discovery data.
> Update data source queries as needed to point to your environment.

---

## Runtime Telemetry (Generated Each Run)

NSO-Rocket writes compact telemetry artifacts during each run. These are meant to be polled by dashboards (Grafana), n8n, or other automations.

**Files**
- `dashboards/data/drift-health.json` — **latest drift snapshot**
  - `run_id` (UTC ISO8601)
  - `simulated_drift` (bool)
  - `totals.{devices,in_topology,not_in_topology}`
  - `by_role.<role>.{devices,in_topology,not_in_topology}`
  - `severity.totals` (e.g. `{critical,high,medium,low}`)
  - `not_in_topology` (list of hostnames)
  - `not_in_topology_detail[]` — objects `{hostname, role, severity}`

- `dashboards/data/drift-history.csv` — **trend log**
  - Columns: `ts,devices,in_topology,not_in_topology,simulated_drift`
  - Existing files are auto-migrated to include the new `simulated_drift` column.

- `dashboards/data/service-timings.csv` — **per-run timings**
  - Columns: `ts,label,ms` (e.g., `remediation:ConfigBackup`, `audit:DriftDetection`, `services_phase`)

- `dashboards/data/discovery.json` — **inventory snapshot**
  - Array of `{hostname, ip, role, os, version}`

> **Note:** `dashboards/drift-health.json` (static dashboard definition) is separate from `dashboards/data/drift-health.json` (runtime telemetry).

---

## Environment Variables

- `NSO_VERBOSE=1` — verbose console output (debug prints)
- `SLACK_WEBHOOK=https://hooks.slack.com/services/...` — optional Slack alert on drift
- `NSO_SIM_LATENCY_MS=10` — simulate per-device work latency (ms) to make timings visible
- `NSO_SIM_DRIFT="host1,host2"` — simulate drift for listed hostnames (without editing topology)

---

## Run

    python3 -m venv .venv && source .venv/bin/activate
    # pip install -r requirements.txt  # if present
    export NSO_VERBOSE=1
    # optional:
    export NSO_SIM_LATENCY_MS=25
    export NSO_SIM_DRIFT="AccessSwitch2"
    python main.py

---

## Verify

    # Snapshot + role/severity
    sed -n '1,200p' dashboards/data/drift-health.json

    # Trend rows (note simulated_drift column)
    tail -n 5 dashboards/data/drift-history.csv

    # Timings
    tail -n 10 dashboards/data/service-timings.csv

    # Inventory export
    sed -n '1,80p' dashboards/data/discovery.json

---

## Notes

- `dashboards/data/drift-health.json` is **runtime telemetry** (generated per run).
- `dashboards/drift-health.json` is a **static dashboard definition**, separate from telemetry.
- If `NSO_SIM_DRIFT` is set, `simulated_drift: true` is included in the snapshot and the history row marks it accordingly.

---

## Grafana (Infinity fast path – minimal steps)

### 1. Serve the telemetry folder (from repo root):

    python3 -m http.server 8000

### 2. Add an Infinity datasource in Grafana:
- Type: *Infinity*
- Allowed hosts: `localhost:8000`

### 3. Panels & queries

- **Drift % Over Time** (Time series)
    - Query: CSV → `http://localhost:8000/dashboards/data/drift-history.csv`
    - Time field: `ts`
    - Calculated field: `drift_pct = (not_in_topology / devices) * 100`
    - Display `drift_pct` (unit: percent)

- **Top Missing Devices** (Table)
    - Query: JSON → `http://localhost:8000/dashboards/data/drift-health.json`
    - Root: `$.not_in_topology_detail[*]`
    - Show columns: `hostname, role, severity`

- **Severity Breakdown** (Pie/Bar)
    - Query: JSON → `http://localhost:8000/dashboards/data/drift-health.json`
    - Root: `$.severity.totals`
    - Transform: JSON → key/value (key = severity, value = count)

- **Drift by Role** (Bar or Table)
    - Query: JSON → `http://localhost:8000/dashboards/data/drift-health.json`
    - Root: `$.by_role`
    - Transform: JSON → key to field (key = role)
    - Optional calc: `role_drift_pct = (not_in_topology / devices) * 100`

- **Remediation Success** (Stat)
    - Query: JSON → `http://localhost:8000/dashboards/data/drift-health.json`
    - Root: `$.totals`
    - Calculated field: `healthy_pct = (in_topology / devices) * 100`
    - Show `healthy_pct` (unit: percent)