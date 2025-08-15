import csv
import json
import yaml
from pathlib import Path

import os
import datetime
import urllib.request
import sys
import time

def timed_section(label: str):
    """Context manager to time blocks and print duration; also returns ms."""
    class _T:
        def __enter__(self_nonlocal):
            self_nonlocal._t0 = time.perf_counter()
            return self_nonlocal
        def __exit__(self_nonlocal, exc_type, exc, tb):
            self_nonlocal.ms = (time.perf_counter() - self_nonlocal._t0) * 1000.0
            print(f"⏱️  {label} took {self_nonlocal.ms:.1f} ms")
    return _T()

# -------------------------------------------------------------------
# Config / Flags
# -------------------------------------------------------------------
VERBOSE = os.getenv("NSO_VERBOSE", "0") not in ("0", "", "false", "False")
SIM_LAT_MS = float(os.getenv("NSO_SIM_LATENCY_MS", "0"))  # e.g. export NSO_SIM_LATENCY_MS=10
SIM_DRIFT = os.getenv("NSO_SIM_DRIFT", "").split(",") if os.getenv("NSO_SIM_DRIFT") else []
SEVERITY_BY_ROLE = {
    "core": "critical",
    "distribution": "high",
    "dist": "high",      # alias if you ever use "dist"
    "access": "medium",
    "edge": "medium",
    "unknown": "low",
}

# File paths
DEVICE_INVENTORY_FILE = Path("examples/demo-environments/device-inventory.csv")
SERVICE_CATALOG_FILE = Path("examples/demo-environments/services.yaml")
TOPOLOGY_FILE = Path("examples/demo-environments/sample-topology.json")

def compute_role_breakdown(devices, missing_set):
    """
    Return per-role counts of total, in_topology, and not_in_topology.
    missing_set: set of hostnames that are missing from topology.
    """
    by_role = {}
    for d in devices:
        role = (d.get("role") or "unknown").strip() or "unknown"
        name = d.get("hostname")
        bucket = by_role.setdefault(role, {"devices": 0, "in_topology": 0, "not_in_topology": 0})
        bucket["devices"] += 1
        if name in missing_set:
            bucket["not_in_topology"] += 1
        else:
            bucket["in_topology"] += 1
    return by_role

def write_drift_summary(not_in_topology, devices, simulated=False):
    """Emit drift summary + by-role + severity buckets, with optional Slack ping."""
    missing_set = set(not_in_topology)
    inventory_total = len(devices)

    # by_role breakdown (keeps your previous behavior)
    by_role = compute_role_breakdown(devices, missing_set)

    # severity buckets + detailed list for missing devices
    severity_totals = {}
    not_in_topology_detail = []
    for d in devices:
        name = d.get("hostname")
        if not name or name not in missing_set:
            continue
        role = (d.get("role") or "unknown").strip() or "unknown"
        sev = classify_severity(role)
        severity_totals[sev] = severity_totals.get(sev, 0) + 1
        not_in_topology_detail.append({
            "hostname": name,
            "role": role,
            "severity": sev,
        })

    summary = {
        "run_id": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "simulated_drift": simulated,
        "totals": {
            "devices": inventory_total,
            "in_topology": inventory_total - len(missing_set),
            "not_in_topology": len(missing_set),
        },
        "by_role": by_role,  # role-level counts (v1.0 enabler)
        "severity": {        # new: severity buckets (v1.0 → Dashboards)
            "totals": severity_totals,       # e.g., {"critical":1,"high":2,"medium":0,"low":0}
            "policy": "by_role",             # documents how buckets were computed
        },
        "not_in_topology": sorted(list(missing_set)),         # keep legacy array for compatibility
        "not_in_topology_detail": not_in_topology_detail,     # objects w/ role+severity
    }

    out = Path("dashboards") / "data" / "drift-health.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(f"\n📝 Wrote drift summary → {out}")

    # Optional Slack webhook notification (adds severity totals if any)
    webhook = os.getenv("SLACK_WEBHOOK", "").strip()
    if webhook:
        sev_text = ", ".join(f"{k}:{v}" for k, v in sorted(severity_totals.items())) or "none"
        payload = {
            "text": (
                f"NSO-Rocket Drift: {summary['totals']['not_in_topology']} of "
                f"{summary['totals']['devices']} missing. Severity: {sev_text}"
            )
        }
        req = urllib.request.Request(
            webhook,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(req, timeout=5)
            print("📣 Slack: drift summary sent.")
        except Exception as e:
            print(f"⚠️ Slack webhook failed: {e}")

def append_drift_history(not_in_topology_count, total_devices, simulated: bool = False):
    """Append a history record for trend charts, with migration-safe support for a new 'simulated_drift' column."""
    hist_dir = Path("dashboards") / "data"
    hist_dir.mkdir(parents=True, exist_ok=True)
    hist_file = hist_dir / "drift-history.csv"
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

    new_header = ["ts", "devices", "in_topology", "not_in_topology", "simulated_drift"]

    def write_row(writer):
        writer.writerow([
            ts,
            str(total_devices),
            str(total_devices - not_in_topology_count),
            str(not_in_topology_count),
            "true" if simulated else "false",
        ])

    if not hist_file.exists():
        # Fresh file with new header
        with open(hist_file, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(new_header)
            write_row(w)
        if VERBOSE:
            print(f"🗂️  Created drift history with header → {hist_file}")
        return

    # File exists — check header and migrate if needed
    with open(hist_file, "r", newline="") as f:
        reader = csv.reader(f)
        try:
            current_header = next(reader)
        except StopIteration:
            current_header = []

        if current_header == new_header:
            # Already on new schema → append
            with open(hist_file, "a", newline="") as af:
                w = csv.writer(af)
                write_row(w)
            if VERBOSE:
                print(f"🗂️  Appended drift history → {hist_file}")
            return

        # If header is old schema (no simulated_drift), migrate in-place
        # Accept old headers with/without spaces; default to old if 4 cols
        if len(current_header) == 4 and [h.strip() for h in current_header] == ["ts", "devices", "in_topology", "not_in_topology"]:
            rows = [row for row in reader]  # remaining old rows
            with open(hist_file, "w", newline="") as wf:
                w = csv.writer(wf)
                w.writerow(new_header)
                # Copy old rows and add simulated_drift=false
                for row in rows:
                    # Pad/trim defensively to 4 cols
                    row = (row + [""] * 4)[:4]
                    w.writerow(row + ["false"])
                # Write the new row
                write_row(w)
            if VERBOSE:
                print(f"🔧 Migrated drift history schema and appended → {hist_file}")
            return

        # Unknown header; fall back to append a new file next to it
        backup = hist_file.with_suffix(".csv.bak")
        hist_file.replace(backup)
        with open(hist_file, "w", newline="") as wf:
            w = csv.writer(wf)
            w.writerow(new_header)
            write_row(w)
        print(f"⚠️ Unrecognized drift-history header. Backed up old file to {backup} and started a new one.")

def append_timing_history(label: str, ms: float):
    """Append a timing datapoint to dashboards/data/service-timings.csv."""
    hist_dir = Path("dashboards") / "data"
    hist_dir.mkdir(parents=True, exist_ok=True)
    f = hist_dir / "service-timings.csv"
    is_new = not f.exists()
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(f, "a", newline="") as fh:
        w = csv.writer(fh)
        if is_new:
            w.writerow(["ts", "label", "ms"])
        w.writerow([ts, label, f"{ms:.3f}"])
    if VERBOSE:
        print(f"🗂️  Appended timing → {f}")

def classify_severity(role: str) -> str:
    """Return severity label based on device role."""
    role_norm = (role or "unknown").strip().lower()
    return SEVERITY_BY_ROLE.get(role_norm, "low")

def write_discovery(devices):
    """
    Emit dashboards/data/discovery.json with current inventory snapshot.
    Fields: hostname, ip, role, os, version.
    """
    out_dir = Path("dashboards") / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "discovery.json"

    payload = []
    for d in devices:
        payload.append({
            "hostname": d.get("hostname"),
            "ip": d.get("ip"),
            "role": d.get("role"),
            "os": d.get("os"),
            "version": d.get("version"),
        })

    out_file.write_text(json.dumps(payload, indent=2))
    if VERBOSE:
        print(f"🧭 Wrote discovery snapshot → {out_file}")

def load_device_inventory():
    if not DEVICE_INVENTORY_FILE.exists():
        print(f"❌ Missing inventory file: {DEVICE_INVENTORY_FILE}")
        return []
    devices = []
    with open(DEVICE_INVENTORY_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Normalize common fields defensively
            row["hostname"] = row.get("hostname", "").strip()
            row["ip"] = row.get("ip", "").strip()
            row["role"] = row.get("role", "").strip()
            if row["hostname"]:
                devices.append(row)
    if VERBOSE and devices:
        print("🧪 DEBUG: First device record:")
        print(devices[0])
    return devices


def load_service_catalog():
    if not SERVICE_CATALOG_FILE.exists():
        print(f"❌ Missing service catalog: {SERVICE_CATALOG_FILE}")
        return []
    with open(SERVICE_CATALOG_FILE, "r") as f:
        data = yaml.safe_load(f) or []
    return data


def load_topology():
    if not TOPOLOGY_FILE.exists():
        print(f"❌ Missing topology file: {TOPOLOGY_FILE}")
        return {"nodes": []}
    with open(TOPOLOGY_FILE, "r") as f:
        data = json.load(f)
    if "nodes" not in data or not isinstance(data["nodes"], list):
        # Keep shape consistent
        data = {"nodes": data.get("nodes", [])}
    return data


def detect_drift(devices, topology):
    """
    Compares devices in inventory vs. devices in topology.
    Flags any missing or extra devices.
    """
    inventory_names = {d.get("hostname", "") for d in devices if d.get("hostname")}
    # sample-topology.json uses node["name"]
    topology_names = {n.get("name", "") for n in topology.get("nodes", []) if n.get("name")}

    missing_in_topology = inventory_names - topology_names
    missing_in_topology |= {h.strip() for h in SIM_DRIFT if h.strip()}
    missing_in_inventory = topology_names - inventory_names

    if VERBOSE:
        print("🧪 DEBUG: inventory_names:", sorted(inventory_names))
        print("🧪 DEBUG: topology_names:", sorted(topology_names))

    return missing_in_topology, missing_in_inventory


def main():
    print("\n🚀 NSO-Rocket – Multi-Workflow Runner\n")
    if SIM_DRIFT:
        print(f"⚠️  SIM_DRIFT active: {', '.join(SIM_DRIFT)}")
    else:
        print("ℹ️  SIM_DRIFT not set")

    # 1) Load and display device inventory
    devices = load_device_inventory()
    print(f"📡 Devices in inventory: {len(devices)}")
    for d in devices:
        print(f" - {d.get('hostname','?')} ({d.get('ip','?')})")

    # 2) Load and display service catalog
    catalog = load_service_catalog()
    print(f"\n🗂️  Services available: {len(catalog)}")

    with timed_section("services_phase") as T_SERV:
        for svc in catalog:
            if VERBOSE:
                print("🧪 DEBUG: Raw service entry:")
                print(svc)

            name = svc.get("name", "unnamed")
            stype = svc.get("type", "unknown")
            target_role = svc.get("target_role", "all")
            print(f" - {name} | Type: {stype}")

            if stype == "remediation":
                with timed_section(f"remediation:{name}") as t:
                    print(f"   🛠 Running remediation: {name}...")
                    for d in devices:
                        if target_role == "all" or d.get("role") == target_role:
                            print(f"     🔧 Backing up config from {d.get('hostname','?')} [{d.get('ip','?')}]...")
                            if SIM_LAT_MS > 0:
                                time.sleep(SIM_LAT_MS / 1000.0)
                try:
                    append_timing_history(f"remediation:{name}", t.ms)
                except Exception as _e:
                    if VERBOSE:
                        print(f"⚠️ timing log failed: {_e}")
                print(f"   ✅ {name} completed.\n")

            elif stype == "audit":
                with timed_section(f"audit:{name}") as t:
                    print(f"   🔍 Running audit: {name}...")
                    for d in devices:
                        if target_role == "all" or d.get("role") == target_role:
                            print(f"     📋 Auditing config of {d.get('hostname','?')} [{d.get('ip','?')}] against source of truth...")
                            if SIM_LAT_MS > 0:
                                time.sleep(SIM_LAT_MS / 1000.0)
                try:
                    append_timing_history(f"audit:{name}", t.ms)
                except Exception as _e:
                    if VERBOSE:
                        print(f"⚠️ timing log failed: {_e}")
                print(f"   ✅ {name} completed.\n")

            else:
                print(f"   ⚠️ Unknown service type: {stype}\n")

    # After the loop, record the whole services phase
    try:
        append_timing_history("services_phase", T_SERV.ms)
    except Exception as _e:
        if VERBOSE:
            print(f"⚠️ timing log failed: {_e}")

    # 3) Load topology and perform drift detection
    topology = load_topology()
    missing_topo, missing_inventory = detect_drift(devices, topology)

    print("\n🔍 Drift Detection Results:")
    if missing_topo:
        print(f" - Devices in inventory but NOT in topology: {sorted(missing_topo)}")
    if missing_inventory:
        print(f" - Devices in topology but NOT in inventory: {sorted(missing_inventory)}")
    if not missing_topo and not missing_inventory:
        print(" ✅ No drift detected! Inventory and topology are aligned.")

    # 4) Wrap up and emit runtime telemetry + optional Slack
    write_drift_summary(missing_topo, devices, simulated=bool(SIM_DRIFT))
    append_drift_history(len(missing_topo), len(devices), simulated=bool(SIM_DRIFT))
    write_discovery(devices)

    print("\n✅ Workflow execution complete.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❗ Unhandled error: {e}")
        sys.exit(1)