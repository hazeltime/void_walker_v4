"""
Migrate Old Config File to Numeric Format

Converts old letter-based values to numeric:
- mode: t -> 1, d -> 2
- disk: auto -> 1, ssd -> 2, hdd -> 3
- strategy: auto -> 1, bfs -> 2, dfs -> 3
"""
import json
import os
import shutil

config_file = "void_walker_config.json"

if not os.path.exists(config_file):
    print(f"[i] No config file found at {config_file}")
    print("    Nothing to migrate")
    exit(0)

# Backup
backup_file = config_file + ".backup"
shutil.copy(config_file, backup_file)
print(f"[+] Created backup: {backup_file}")

# Load
with open(config_file, 'r') as f:
    config = json.load(f)

print(f"\n[*] Original config:")
for key, value in config.items():
    print(f"    {key:20} : {value}")

# Migrate
changed = False

if "mode" in config:
    old = config["mode"]
    if old == "t":
        config["mode"] = "1"
        changed = True
        print(f"\n[>] mode: {old} -> 1")
    elif old == "d":
        config["mode"] = "2"
        changed = True
        print(f"\n[>] mode: {old} -> 2")

if "disk" in config:
    old = config["disk"]
    if old == "auto":
        config["disk"] = "1"
        changed = True
        print(f"[>] disk: {old} -> 1")
    elif old == "ssd":
        config["disk"] = "2"
        changed = True
        print(f"[>] disk: {old} -> 2")
    elif old == "hdd":
        config["disk"] = "3"
        changed = True
        print(f"[>] disk: {old} -> 3")

if "strategy" in config:
    old = config["strategy"]
    if old == "auto":
        config["strategy"] = "1"
        changed = True
        print(f"[>] strategy: {old} -> 1")
    elif old == "bfs":
        config["strategy"] = "2"
        changed = True
        print(f"[>] strategy: {old} -> 2")
    elif old == "dfs":
        config["strategy"] = "3"
        changed = True
        print(f"[>] strategy: {old} -> 3")

if changed:
    # Save
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n[✓] Updated config:")
    for key, value in config.items():
        print(f"    {key:20} : {value}")
    
    print(f"\n[OK] Migration complete!")
    print(f"     Backup saved as: {backup_file}")
else:
    print("\n[i] Config already uses numeric format - no changes needed")
