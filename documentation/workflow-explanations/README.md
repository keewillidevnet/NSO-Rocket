# 📜 Workflow Explanations

This section provides high-level explanations of each workflow in **NSO‑Rocket**.

---

## ✅ Compliance
### **Config Drift Detection**
- **Purpose:** Detects configuration drift by comparing NSO intended configs with live device configs.
- **Key Features:**  
  - Async polling (configurable via `configs/async-settings.json`)  
  - Topology-aware severity scoring (`configs/topology-weights.json`)  
  - Slack alerts & dashboard output (`dashboards/drift-health.json`)
- **File:** [`workflows/compliance/config-drift-detection.json`](../../workflows/compliance/config-drift-detection.json)

---

## 🔍 Discovery
### **Network Discovery**
- **Purpose:** Scans NSO and live network to discover unregistered devices/services.
- **Key Features:**  
  - Generates discovery report (`dashboards/discovery-health.json`)  
  - Populates inventory for onboarding
- **File:** [`workflows/discovery/network-discovery.json`](../../workflows/discovery/network-discovery.json)

---

## 🔄 Remediation (Planned)
- **Purpose:** Applies automated or semi-automated fixes for detected drift.
- **Status:** Placeholder in `workflows/operations/` for Phase 1.5.

---

## 🔗 Integration (Planned)
- **Purpose:** Connect NSO‑Rocket workflows with external systems (ITSM, legacy APIs).
- **Status:** Placeholder in `workflows/integration/`.

---

## 📊 Monitoring (Planned)
- **Purpose:** Real-time performance and compliance monitoring dashboards.
- **Status:** Placeholder in `workflows/monitoring/`.

---

## ⚙️ Operations (Planned)
- **Purpose:** Service deployment, rollback, and operational workflows.
- **Status:** Placeholder in `workflows/operations/`.
