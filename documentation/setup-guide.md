# 🛠 NSO‑Rocket Setup Guide

This guide will help you install, configure, and run **NSO‑Rocket** in your environment.

---

## 1️⃣ Prerequisites
Ensure you have the following installed:
- **Cisco NSO** (version 5.7+ recommended)
- **n8n** (v1.0+; [Installation Guide](https://docs.n8n.io/getting-started/installation/))
- **Git** (for cloning repo)
- *(Optional)* **Grafana** (for dashboards)

---

## 2️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/NSO-Rocket.git
cd NSO-Rocket
```

---

## 3️⃣ Open in VSCode
```bash
code .
```

---

## 4️⃣ Configure NSO‑Rocket
### Async Settings
Edit `configs/async-settings.json` to tune:
- `batchSize` (number of devices processed at a time)
- `concurrentRequests` (parallel API calls)
- `timeoutSeconds` (per request)

### Topology Weights
Edit `configs/topology-weights.json` to adjust severity weighting:
- `core`, `distribution`, `access`, `lab`

---

## 5️⃣ Import Workflows into n8n
- In n8n, click **Import Workflow**
- Select `workflows/compliance/config-drift-detection.json`
- (Optional) Import discovery & remediation workflows

---

## 6️⃣ Connect Integrations
- Configure **Slack API** (alerts)
- Connect **Grafana** or n8n dashboard for drift visualizations

---

## 7️⃣ Run Drift Detection
- Trigger drift detection workflow in n8n
- View Slack alerts and dashboards for results

---

## ✅ Next Steps
- Explore `documentation/troubleshooting.md` for common fixes
- Check `agntcy/manifests/` for multi‑agent orchestration details