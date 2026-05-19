#!/usr/bin/env python3
"""
mdm_detect.py -- Detect MDM (Mobile Device Management) servers and restrictions
Analyzes installed profiles, trust anchors, and network traffic interception
"""
import subprocess, sys, json, re
from pathlib import Path

def check_mdm():
    """Check for MDM on jailbroken/semi-tethered iOS via SSH"""
    results = {
        "mdm_profiles": [],
        "trust_anchors": [],
        "network_proxies": [],
        "suspicious_daemons": [],
        "restriction_files": [],
    }
    
    # Check for MDM profile installation markers
    mdm_markers = [
        "/var/mobile/Library/ConfigurationProfiles/Settings/.profileInstalled",
        "/var/Managed\ Preferences",
        "/Library/ManagedPreferences",
    ]
    
    for marker in mdm_markers:
        try:
            r = subprocess.run(f"ssh root@localhost test -f '{marker}'", 
                             shell=True, capture_output=True, timeout=2)
            if r.returncode == 0:
                results["mdm_profiles"].append(marker)
        except:
            pass
    
    # Check mitmproxy/network interception
    proxy_check = subprocess.run(
        "ssh root@localhost grep -r 'proxy' /var/lib/networkd 2>/dev/null || true",
        shell=True, capture_output=True, timeout=2, text=True
    )
    if proxy_check.stdout:
        results["network_proxies"] = proxy_check.stdout.splitlines()
    
    # List trust anchors (CA certs)
    certs = subprocess.run(
        "ssh root@localhost ls /var/keychains/ 2>/dev/null || true",
        shell=True, capture_output=True, timeout=2, text=True
    )
    results["trust_anchors"] = certs.stdout.splitlines()
    
    # Look for MDM daemons
    mdm_daemons = ["profiled", "mobileSafari", "uicache"]
    ps_output = subprocess.run(
        "ssh root@localhost ps aux 2>/dev/null || true",
        shell=True, capture_output=True, timeout=2, text=True
    )
    for line in ps_output.stdout.splitlines():
        for daemon in mdm_daemons:
            if daemon in line.lower() and "mdm" not in line.lower():
                results["suspicious_daemons"].append(line)
    
    return results

def print_report(results):
    print("\n🔍 MDM Detection Report")
    print("=" * 50)
    
    if results["mdm_profiles"]:
        print("\n⚠️  MDM Profiles installed:")
        for p in results["mdm_profiles"]:
            print(f"    {p}")
    else:
        print("\n✅ No MDM profiles detected")
    
    if results["trust_anchors"]:
        print(f"\n📜 Trust Anchors ({len(results['trust_anchors'])}):")
        for a in results["trust_anchors"][:5]:
            print(f"    {a}")
        if len(results["trust_anchors"]) > 5:
            print(f"    ... and {len(results['trust_anchors'])-5} more")
    
    if results["network_proxies"]:
        print(f"\n🌐 Network Proxies detected:")
        for p in results["network_proxies"]:
            print(f"    {p}")
    
    print(f"\n📊 Summary:")
    print(f"    Profiles: {len(results['mdm_profiles'])}")
    print(f"    CAs: {len(results['trust_anchors'])}")
    print(f"    Proxies: {len(results['network_proxies'])}")

if __name__ == "__main__":
    print("🔐 MDM Detector — requires SSH root access to device")
    try:
        results = check_mdm()
        print_report(results)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
