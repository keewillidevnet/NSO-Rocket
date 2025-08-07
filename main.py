import csv
import json
import yaml
from pathlib import Path

# File paths
DEVICE_INVENTORY_FILE = Path("examples/demo-environments/device-inventory.csv")
SERVICE_CATALOG_FILE = Path("examples/demo-environments/services.yaml")
TOPOLOGY_FILE = Path("examples/demo-environments/sample-topology.json")


def load_device_inventory():
    devices = []
    with open(DEVICE_INVENTORY_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            devices.append(row)
    return devices


def load_service_catalog():
    with open(SERVICE_CATALOG_FILE, "r") as f:
        return yaml.safe_load(f)


def load_topology():
    with open(TOPOLOGY_FILE, "r") as f:
        return json.load(f)


def detect_drift(devices, topology):
    """
    Compares devices in inventory vs. devices in topology.
    Flags any missing or extra devices.
    """
    print("🧪 DEBUG: Device record structure:")
    print(devices[0])

    inventory_names = {d["hostname"] for d in devices}
    topology_names = {n["name"] for n in topology.get("nodes", [])}

    missing_in_topology = inventory_names - topology_names
    missing_in_inventory = topology_names - inventory_names

    return missing_in_topology, missing_in_inventory


def main():
    print("\n🚀 NSO-Rocket – Multi-Workflow Runner\n")

    # 1. Load and display device inventory
    devices = load_device_inventory()
    print(f"📡 Devices in inventory: {len(devices)}")
    for d in devices:
        print(f" - {d['hostname']} ({d['ip']})")

    # 2. Load and display service catalog
    catalog = load_service_catalog()
    print(f"\n🗂️  Services available: {len(catalog)}")
    for svc in catalog:
        print("🧪 DEBUG: Raw service entry:")
        print(svc)
        print(f" - {svc['name']} | Type: {svc['type']}")

        # Trigger logic based on service type
        if svc["type"] == "remediation":
            print(f"   🛠 Running remediation: {svc['name']}...")
            for d in devices:
                if svc["target_role"] == "all" or d["role"] == svc["target_role"]:
                    print(f"     🔧 Backing up config from {d['hostname']} [{d['ip']}]...")
            print(f"   ✅ {svc['name']} completed.\n")

        elif svc["type"] == "audit":
            print(f"   🔍 Running audit: {svc['name']}...")
            for d in devices:
                if d["role"] == svc["target_role"]:
                    print(f"     📋 Auditing config of {d['hostname']} [{d['ip']}] against source of truth...")
            print(f"   ✅ {svc['name']} completed.\n")

        else:
            print(f"   ⚠️ Unknown service type: {svc['type']}\n")

    # 3. Load topology and perform drift detection
    topology = load_topology()
    missing_topo, missing_inventory = detect_drift(devices, topology)

    print("\n🔍 Drift Detection Results:")
    if missing_topo:
        print(f" - Devices in inventory but NOT in topology: {sorted(missing_topo)}")
    if missing_inventory:
        print(f" - Devices in topology but NOT in inventory: {sorted(missing_inventory)}")
    if not missing_topo and not missing_inventory:
        print(" ✅ No drift detected! Inventory and topology are aligned.")

    print("\n✅ Workflow execution complete.\n")


if __name__ == "__main__":
    main()
