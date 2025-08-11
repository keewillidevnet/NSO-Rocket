# 🚀 NSO‑Rocket
![CI](https://github.com/keewillidevnet/NSO-Rocket/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![AGNTCY](https://img.shields.io/badge/AGNTCY-compatible-orange)
![n8n](https://img.shields.io/badge/n8n-workflows-success)
![NSO](https://img.shields.io/badge/Cisco-NSO-lightgrey)
![Version](https://img.shields.io/badge/version-1.0.0-blueviolet)

**Key Files**
- 📘 [Setup Guide](documentation/setup-guide.md)
- ⚡ [Flagship Drift Workflow](workflows/compliance/config-drift-detection.json)
- 🤖 [AGNTCY Drift Agent Manifest](agntcy/manifests/drift-detection-workflow.yaml)

> **Launch NSO to new heights with AGNTCY multi‑agents & n8n automation**
> _Transform NSO operations with intelligent multi‑agent automation. Combines AGNTCY's agent framework with n8n workflows to eliminate config drift, accelerate deployments & reduce complexity._

---

## Overview

**NSO‑Rocket** supercharges Cisco NSO deployments by integrating:
- **n8n Workflows** for automation
- **AGNTCY Multi‑Agent Framework** for intelligence & orchestration
- **Async + Topology‑Aware Drift Detection** for performance
- **Dashboards** for real‑time visibility

Designed for **enterprise network teams** and **automation engineers** who need speed, intelligence, and reliability in their NSO environments.

---

## Repository Structure

```plaintext
NSO-Rocket/
├── workflows/            # n8n workflows (discovery, compliance, monitoring, operations)
│   ├── compliance/       # Drift detection, standardization, remediation
│   ├── discovery/        # Brownfield network scan & service discovery
│   ├── integration/      # Legacy bridges & API translation
│   ├── monitoring/       # Performance metrics & health dashboards
│   └── operations/       # Service deployment & rollback
├── agntcy/               # AGNTCY multi‑agent definitions
│   ├── schemas/          # OASF agent schemas
│   ├── agents/           # Multi‑agent configurations
│   └── manifests/        # Agent workflow manifests
├── configs/              # Async & topology weighting configs
├── dashboards/           # Grafana/n8n dashboards
├── documentation/        # Setup, workflow guides, troubleshooting
├── scripts/              # Helper & transformer scripts
├── templates/            # Device configs, service templates, YANG models
└── examples/             # Demo environments & use case scenarios
```

---

## Key Features

- ✅ **Async Drift Detection** — Parallel API calls for lightning-fast checks
- ✅ **Topology-Aware Prioritization** — Core devices prioritized automatically
- ✅ **Multi-Agent Orchestration** — AGNTCY semantic routing & workflow chaining
- ✅ **Dashboards** — Real-time drift trends, compliance health, remediation history
- ✅ **Multi-Vendor Ready** — Templates & workflows for Cisco, Juniper, Arista, more
- ✅ **Brownfield Discovery** — Migrate existing services into NSO with minimal friction

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/NSO-Rocket.git
cd NSO-Rocket
```

### 2. Open in VSCode
```bash
code .
```

### 3. Setup Environment
- Install **n8n** ([installation guide](https://docs.n8n.io/getting-started/installation/))
- Configure **NSO API credentials** in `configs/async-settings.json`
- Adjust **topology weights** in `configs/topology-weights.json`

### 4. Import Workflows
- In n8n, import workflows from `workflows/` (start with `compliance/config-drift-detection.json`)

### 5. Run Drift Detection
- Trigger drift detection workflow in n8n
- View results in Slack (alerts) or Grafana (dashboards in `dashboards/`)

---

## Integrations

- **Cisco NSO** — API integration for device configs & service state
- **n8n** — Workflow engine for orchestration & automation
- **AGNTCY** — Multi‑agent interoperability & semantic routing
- **Grafana** — Optional visualization for drift, compliance, and health trends

---

## Roadmap

| Version | Highlights |
|---------|------------|
| **v1.0** | 🔍 **Async drift detection**<br>📊 Topology prioritization<br>📈 Dashboards<br>📂 AGNTCY schemas |
| **v1.5** | 🛠 **Remediation workflows**<br>✅ Approval gates<br>🔗 ITSM integration *(ServiceNow / Jira)* |
| **v2.0** | 🤖 **Full AGNTCY workflow orchestration**<br>🛡 Remediation agents<br>🚚 Brownfield migration automation |

---

## License
MIT License — see [LICENSE](LICENSE)

---

## Contributing
Pull requests welcome! Check `documentation/setup-guide.md` for contribution guidelines.
<!-- register Basic Test / placeholder-tests (pull_request) -->
