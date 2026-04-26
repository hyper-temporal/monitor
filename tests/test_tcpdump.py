#!/usr/bin/env python3
"""
Test tcpdump to see what actual JSON structure looks like.
Run this to discover the correct field mappings.
"""

import subprocess
import json
import sys

def test_tcpdump():
    """Capture one packet and show its structure."""
    print("🔍 Testing tcpdump on en0...")
    print("  (This will capture 1 ICMP packet via ping)")
    print("")
    
    # Start tcpdump in background, capture 1 packet
    # -j flag outputs JSON
    # -i interface to capture from
    cmd = [
        "sudo",
        "tcpdump",
        "-i", "en0",
        "-j", 
        "-c", "1",  # Capture 1 packet
        "-n",       # Don't resolve names
        "icmp"      # Filter for ICMP (ping)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("")
    print("⏳ Send a ping from another terminal:")
    print("   ping 8.8.8.8")
    print("")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # tcpdump outputs to stderr
        output = result.stderr or result.stdout
        
        print("📦 Raw tcpdump output:")
        print(output)
        print("")
        
        # Try to parse JSON
        if output.strip():
            try:
                # tcpdump might output multiple lines, each could be JSON
                for line in output.split('\n'):
                    if line.strip() and line.startswith('{'):
                        pkt = json.loads(line)
                        print("✓ Valid JSON found!")
                        print("")
                        print("📊 Packet structure (first level keys):")
                        for key in pkt.keys():
                            print(f"   - {key}")
                        print("")
                        
                        # Pretty print
                        print("🔎 Full packet structure:")
                        print(json.dumps(pkt, indent=2)[:1000])  # First 1000 chars
                        print("")
                        
                        # Try to find IP addresses
                        print("🔍 Trying to find IP fields...")
                        def find_ips(obj, path=""):
                            if isinstance(obj, dict):
                                for k, v in obj.items():
                                    new_path = f"{path}.{k}" if path else k
                                    if isinstance(v, str) and '.' in v and all(x.isdigit() or x == '.' for x in v):
                                        print(f"   Found IP at: {new_path} = {v}")
                                    elif isinstance(v, (dict, list)):
                                        find_ips(v, new_path)
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    find_ips(item, f"{path}[{i}]")
                        
                        find_ips(pkt)
                        return
                        
            except json.JSONDecodeError as e:
                print(f"✗ Could not parse as JSON: {e}")
        
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout - no packet captured. Did you run 'ping 8.8.8.8' in another terminal?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_tcpdump()
