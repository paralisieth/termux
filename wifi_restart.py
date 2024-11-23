#!/data/data/com.termux/files/usr/bin/python

import os
import time
import json
import subprocess
import argparse

def check_termux_packages():
    """Check if required Termux API packages are installed"""
    try:
        subprocess.run(['termux-wifi-connectioninfo'], capture_output=True)
    except FileNotFoundError:
        print("⚠️ Termux API not found!")
        print("\nPlease install required packages with:")
        print("pkg install termux-api")
        return False
    return True

def get_wifi_info():
    """Get current WiFi connection information"""
    try:
        result = subprocess.run(['termux-wifi-connectioninfo'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except:
        return None

def restart_wifi():
    """Restart WiFi connection"""
    print("📱 Restarting WiFi...")
    
    # Disable WiFi
    print("→ Disabling WiFi...")
    subprocess.run(['termux-wifi-enable', 'false'])
    time.sleep(2)  # Wait for WiFi to fully disable
    
    # Enable WiFi
    print("→ Enabling WiFi...")
    subprocess.run(['termux-wifi-enable', 'true'])
    time.sleep(5)  # Wait for WiFi to reconnect
    
    # Check new connection
    new_info = get_wifi_info()
    if new_info and new_info.get('ssid'):
        print(f"✅ Successfully reconnected to: {new_info['ssid']}")
    else:
        print("❌ Failed to reconnect to WiFi")

def main():
    parser = argparse.ArgumentParser(description='Restart WiFi connection in Termux')
    parser.add_argument('-f', '--force', action='store_true', 
                       help='Force restart without confirmation')
    args = parser.parse_args()
    
    # Check for required packages
    if not check_termux_packages():
        return
    
    # Get current WiFi info
    wifi_info = get_wifi_info()
    
    if not wifi_info:
        print("❌ Not connected to any WiFi network")
        return
    
    ssid = wifi_info.get('ssid', 'Unknown')
    print(f"\nCurrently connected to: {ssid}")
    
    # Ask for confirmation unless force flag is used
    if not args.force:
        confirm = input("\nDo you want to restart the WiFi connection? (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled")
            return
    
    restart_wifi()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
