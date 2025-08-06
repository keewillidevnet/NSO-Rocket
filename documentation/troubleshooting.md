# 🛠 NSO‑Rocket Troubleshooting Guide

This guide covers common issues when running **NSO‑Rocket** and how to fix them.

---

## 1️⃣ General Checks
Before troubleshooting, verify:
- NSO is **running** and API endpoint is reachable.
- n8n instance is **online** and workflows are **enabled**.
- `configs/async-settings.json` is **valid JSON** (syntax errors will break workflows).

---

## 2️⃣ Common Issues

### ❌ Drift Detection Workflow Fails to Start
**Cause:** Missing or incorrect NSO API credentials  
**Fix:**
- Check `configs/async-settings.json` for `baseUrl` and authentication details.
- Test NSO API with `curl`:
```bash
curl -k -u <user>:<pass> https://nso.example.com/api
```

---

### ❌ No Drift Alerts in Slack
**Cause:** Slack API token not configured or wrong channel name  
**Fix:**
- Update Slack credentials in n8n’s Slack node.
- Ensure the Slack bot is invited to the alert channel:
```text
/invite @YourSlackBot
```

---

### ❌ Grafana Dashboard Shows No Data
**Cause:** Data source not connected or log path incorrect  
**Fix:**
- Check `dashboards/drift-health.json` for correct datasource IDs.
- Verify log file output directory in `configs/async-settings.json` (`logFilePath`).

---

### ❌ Discovery Workflow Returns Empty
**Cause:** No devices discovered in current NSO inventory  
**Fix:**
- Verify `workflows/discovery/network-discovery.json` has correct API endpoints.
- Check NSO device list via:
```bash
ncs_cli -C -u admin
devices list
```

---

## 3️⃣ Tips for Debugging in n8n
- Enable **Workflow Execution Logs** in n8n settings.
- Use **“Execute Node”** on specific nodes to isolate failures.
- Check n8n’s **system logs** for detailed error messages.

---

## ✅ When to Escalate
If the above steps don’t fix the issue:
- Open a GitHub issue with:
  - Workflow name
  - n8n execution logs
  - NSO version
  - JSON config files (redact credentials)