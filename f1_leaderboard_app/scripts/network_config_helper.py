#!/usr/bin/env python3
"""
F1 Leaderboard - Network Configuration Helper

This script helps switch between shop and mobile network configurations.
Perfect for taking the setup to different events with different routers.

Usage:
    python scripts/network_config_helper.py --show-current
    python scripts/network_config_helper.py --set-profile SHOP
    python scripts/network_config_helper.py --set-profile MOBILE  
    python scripts/network_config_helper.py --generate-batch RIG1
"""

import os
import sys
import argparse

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from config.app_config import NETWORK_CONFIG, SHOP_NETWORK, MOBILE_NETWORK, NETWORK_PROFILE

def show_current_config():
    """Display the current network configuration."""
    print(f"\n=== F1 Leaderboard Network Configuration ===")
    print(f"Active Profile: {NETWORK_PROFILE}")
    print(f"Network Name: {NETWORK_CONFIG['name']}")
    print(f"Network Range: {NETWORK_CONFIG['network_range']}")
    print(f"API Server (Reception Laptop): {NETWORK_CONFIG['api_server_ip']}")
    print(f"Gateway: {NETWORK_CONFIG['gateway']}")
    print(f"Subnet Mask: {NETWORK_CONFIG['subnet_mask']}")
    
    print(f"\nRig IP Assignments:")
    for rig_id, ip in NETWORK_CONFIG['rig_ips'].items():
        print(f"  {rig_id}: {ip}")

def show_all_profiles():
    """Show both available network profiles."""
    print(f"\n=== Available Network Profiles ===")
    
    print(f"\n1. SHOP Profile:")
    print(f"   Name: {SHOP_NETWORK['name']}")
    print(f"   Range: {SHOP_NETWORK['network_range']}")
    print(f"   Reception Laptop: {SHOP_NETWORK['api_server_ip']}")
    print(f"   Rigs: {SHOP_NETWORK['rig_ips']['RIG1']}-{SHOP_NETWORK['rig_ips']['RIG4']}")
    
    print(f"\n2. MOBILE Profile:")
    print(f"   Name: {MOBILE_NETWORK['name']}")
    print(f"   Range: {MOBILE_NETWORK['network_range']}")
    print(f"   Reception Laptop: {MOBILE_NETWORK['api_server_ip']}")
    print(f"   Rigs: {MOBILE_NETWORK['rig_ips']['RIG1']}-{MOBILE_NETWORK['rig_ips']['RIG4']}")
    
    print(f"\nCurrently Active: {NETWORK_PROFILE}")

def set_profile(profile_name):
    """Switch to a different network profile."""
    profile_name = profile_name.upper()
    
    if profile_name not in ["SHOP", "MOBILE"]:
        print(f"Error: Invalid profile '{profile_name}'. Valid profiles: SHOP, MOBILE")
        return
        
    # Read the current config file
    config_path = os.path.join(project_root, "config", "app_config.py")
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Replace the NETWORK_PROFILE line
    import re
    pattern = r'NETWORK_PROFILE = "[^"]*"'
    replacement = f'NETWORK_PROFILE = "{profile_name}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    # Write back the modified content
    with open(config_path, 'w') as f:
        f.write(new_content)
    
    print(f"\n✅ Network profile switched to: {profile_name}")
    print(f"📝 Remember to:")
    print(f"   1. Restart the backend server")
    print(f"   2. Update static IPs on all rig PCs")
    print(f"   3. Generate new batch files if needed")

def generate_batch_config(rig_id):
    """Generate a batch file to configure static IP for a rig."""
    rig_id = rig_id.upper()
    
    if rig_id not in NETWORK_CONFIG['rig_ips']:
        print(f"Error: Unknown rig ID '{rig_id}'. Valid IDs: {list(NETWORK_CONFIG['rig_ips'].keys())}")
        return
    
    rig_ip = NETWORK_CONFIG['rig_ips'][rig_id]
    gateway = NETWORK_CONFIG['gateway']
    profile_name = NETWORK_PROFILE
    
    batch_content = f"""@echo off
echo ==========================================
echo F1 Leaderboard - Network Configuration
echo Profile: {profile_name} ({NETWORK_CONFIG['name']})
echo Rig: {rig_id}
echo ==========================================
echo.
echo Setting IP: {rig_ip}
echo Gateway: {gateway}
echo Subnet: {NETWORK_CONFIG['subnet_mask']}
echo.

REM Get the network adapter name
for /f "tokens=1,2*" %%i in ('netsh interface show interface ^| findstr /C:"Connected"') do (
    set adapter_name=%%k
)

echo Configuring adapter: %adapter_name%
echo.

REM Set static IP
netsh interface ip set address name="%adapter_name%" static {rig_ip} {NETWORK_CONFIG['subnet_mask']} {gateway}

REM Set DNS (Google's public DNS)
netsh interface ip set dns name="%adapter_name%" static 8.8.8.8
netsh interface ip add dns name="%adapter_name%" 8.8.4.4 index=2

echo.
echo ✅ Network configuration complete for {rig_id}!
echo Profile: {profile_name}
echo IP: {rig_ip}
echo Gateway: {gateway}
echo.
echo The rig is now configured for: {NETWORK_CONFIG['name']}
echo.
pause
"""
    
    filename = f"setup_network_{rig_id}_{profile_name}.bat"
    with open(filename, 'w') as f:
        f.write(batch_content)
    
    print(f"\n✅ Generated: {filename}")
    print(f"📋 Run this batch file as administrator on the {rig_id} PC")
    print(f"🌐 This will configure {rig_id} for: {NETWORK_CONFIG['name']}")

def generate_all_batch_files():
    """Generate batch files for all rigs in both network profiles."""
    print("\n=== Generating Network Configuration Batch Files ===\n")
    
    profiles = ["SHOP", "MOBILE"]
    rigs = ["RIG1", "RIG2", "RIG3", "RIG4"]
    
    for profile in profiles:
        # Get the profile config
        if profile == "MOBILE":
            config = MOBILE_NETWORK
        else:
            config = SHOP_NETWORK
        
        print(f"📁 Generating {profile} profile batch files...")
        
        for rig_id in rigs:
            if rig_id not in config['rig_ips']:
                continue
                
            rig_ip = config['rig_ips'][rig_id]
            gateway = config['gateway']
            
            batch_content = f"""@echo off
echo ==========================================
echo F1 Leaderboard - Network Configuration
echo Profile: {profile} ({config['name']})
echo Rig: {rig_id}
echo ==========================================
echo.
echo Setting IP: {rig_ip}
echo Gateway: {gateway}
echo Subnet: {config['subnet_mask']}
echo.

REM Get the network adapter name
for /f "tokens=1,2*" %%i in ('netsh interface show interface ^| findstr /C:"Connected"') do (
    set adapter_name=%%k
)

echo Configuring adapter: %adapter_name%
echo.

REM Set static IP
netsh interface ip set address name="%adapter_name%" static {rig_ip} {config['subnet_mask']} {gateway}

REM Set DNS (Google's public DNS)
netsh interface ip set dns name="%adapter_name%" static 8.8.8.8
netsh interface ip add dns name="%adapter_name%" 8.8.4.4 index=2

echo.
echo ✅ Network configuration complete for {rig_id}!
echo Profile: {profile}
echo IP: {rig_ip}
echo Gateway: {gateway}
echo.
echo The rig is now configured for: {config['name']}
echo.
pause
"""
            
            filename = f"setup_network_{rig_id}_{profile}.bat"
            with open(filename, 'w') as f:
                f.write(batch_content)
            
            print(f"   ✅ {filename}")
    
    print(f"\n🎯 Generated batch files for both network profiles!")
    print(f"📦 Include these files in your installer package.")
    print(f"🔧 Operators can run the appropriate files based on their network profile.")

def main():
    parser = argparse.ArgumentParser(description="F1 Leaderboard Network Configuration Helper")
    parser.add_argument('--show-current', action='store_true', help='Show current network configuration')
    parser.add_argument('--show-all', action='store_true', help='Show all available network profiles')  
    parser.add_argument('--set-profile', choices=['SHOP', 'MOBILE'], help='Switch to a network profile')
    parser.add_argument('--generate-batch', help='Generate network config batch file for specific rig (RIG1, RIG2, etc.)')
    parser.add_argument('--generate-all', action='store_true', help='Generate network config batch files for all rigs in both profiles')
    
    args = parser.parse_args()
    
    if args.show_current:
        show_current_config()
    elif args.show_all:
        show_all_profiles()
    elif args.set_profile:
        set_profile(args.set_profile)
    elif args.generate_batch:
        generate_batch_config(args.generate_batch)
    elif args.generate_all:
        generate_all_batch_files()
    else:
        # Show help and current config by default
        show_current_config()
        print(f"\n" + "="*50)
        parser.print_help()

if __name__ == "__main__":
    main() 