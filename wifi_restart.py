#!/data/data/com.termux/files/usr/bin/python

import os
import time
import json
import subprocess
import argparse
from datetime import datetime

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def clear_screen():
    """Clear terminal screen"""
    os.system('clear')

def print_banner():
    """Print cool ASCII art banner"""
    banner = f"""{Colors.CYAN}
╔══════════════════════════════════════════╗
║     {Colors.YELLOW}▀▛▘  ▗  ▗▜▘▗     {Colors.CYAN}                   ║
║     {Colors.YELLOW}▌▞▀▖▄ ▄▐ ▐ ▄ ▄▌▗▘{Colors.CYAN}                   ║
║     {Colors.YELLOW}▌▌ ▌▐ ▐▐ ▐ ▐ ▛▌▜ {Colors.CYAN}                   ║
║     {Colors.YELLOW}▘▝▀ ▀▄▀▐▄▟▖▀▄▝▘▀▘{Colors.CYAN}                   ║
║        {Colors.BLUE}WiFi Control Center{Colors.CYAN}                  ║
╚══════════════════════════════════════════╝{Colors.RESET}"""
    print(banner)

def check_termux_api():
    """Check if Termux:API is installed"""
    try:
        subprocess.run(['termux-wifi-scaninfo'], 
                      capture_output=True)
        return True
    except FileNotFoundError:
        print(f"\n{Colors.RED}Termux:API not found!{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please install Termux:API app from F-Droid{Colors.RESET}")
        print(f"Then run: {Colors.GREEN}pkg install termux-api{Colors.RESET}")
        return False

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

def scan_networks():
    """Scan for WiFi networks using Termux API"""
    try:
        result = subprocess.run(['termux-wifi-scaninfo'],
                              capture_output=True,
                              text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"{Colors.RED}Error during scan: {str(e)}{Colors.RESET}")
        return None

def print_networks(networks):
    """Print available networks"""
    if not networks:
        print(f"\n{Colors.RED}No networks found{Colors.RESET}")
        return
        
    print(f"\n{Colors.BOLD}Available Networks:{Colors.RESET}")
    for i, net in enumerate(networks, 1):
        ssid = net.get('ssid', 'Hidden Network')
        bssid = net.get('bssid', 'Unknown')
        signal = int(net.get('level', 0))
        freq = net.get('frequency', 0)
        
        # Convert signal strength to bars
        signal_percent = (100 + signal) / 50  # Convert dBm to percentage
        bars = int(signal_percent * 4)
        signal_str = '▂▄▆█'[:bars] + '░' * (4 - bars)
        
        print(f"{i}. {Colors.GREEN}{ssid}{Colors.RESET}")
        print(f"   ├─ BSSID: {bssid}")
        print(f"   ├─ Signal: {signal_str} ({signal} dBm)")
        print(f"   └─ Freq: {freq} MHz")

def toggle_wifi(enable=True):
    """Toggle WiFi on/off"""
    try:
        subprocess.run(['termux-wifi-enable', str(enable).lower()],
                      check=True)
        time.sleep(2)  # Wait for WiFi to change state
        return True
    except:
        return False

def restart_wifi():
    """Restart WiFi connection"""
    print(f"\n{Colors.YELLOW}📱 Restarting WiFi...{Colors.RESET}")
    
    # Disable WiFi
    print(f"{Colors.RED}→ Disabling WiFi...{Colors.RESET}")
    if not toggle_wifi(False):
        print(f"{Colors.RED}Failed to disable WiFi{Colors.RESET}")
        return
    
    time.sleep(2)
    
    # Enable WiFi
    print(f"{Colors.GREEN}→ Enabling WiFi...{Colors.RESET}")
    if not toggle_wifi(True):
        print(f"{Colors.RED}Failed to enable WiFi{Colors.RESET}")
        return
    
    # Wait for connection with animation
    print(f"\n{Colors.CYAN}Waiting for connection...{Colors.RESET}")
    animation = "|/-\\"
    for i in range(10):
        print(f"\r{Colors.CYAN}Connecting... {animation[i % len(animation)]}{Colors.RESET}", 
              end='')
        time.sleep(0.5)
    print()
    
    # Check new connection
    info = get_wifi_info()
    if info and info.get('ssid'):
        print(f"\n{Colors.GREEN}✅ Connected to: {info['ssid']}{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ Not connected to any network{Colors.RESET}")

def print_wifi_info():
    """Print current WiFi connection information"""
    info = get_wifi_info()
    
    if not info:
        print(f"\n{Colors.RED}Not connected to any network{Colors.RESET}")
        return
        
    ssid = info.get('ssid', 'Unknown')
    bssid = info.get('bssid', 'Unknown')
    rssi = info.get('rssi', 0)
    ip = info.get('ip', 'Unknown')
    link_speed = info.get('link_speed', 'Unknown')
    
    # Calculate signal strength
    signal_percent = (100 + rssi) / 50  # Convert dBm to percentage
    bars = int(signal_percent * 4)
    signal_str = '▂▄▆█'[:bars] + '░' * (4 - bars)
    
    print(f"\n{Colors.BOLD}Current Connection:{Colors.RESET}")
    print(f"├─ Network: {Colors.GREEN}{ssid}{Colors.RESET}")
    print(f"├─ BSSID:   {bssid}")
    print(f"├─ Signal:   {signal_str} ({rssi} dBm)")
    print(f"├─ Speed:    {link_speed} Mbps")
    print(f"└─ IP:       {Colors.BLUE}{ip}{Colors.RESET}")

def print_menu():
    """Print interactive menu"""
    print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
    print(f"1. {Colors.GREEN}Restart WiFi{Colors.RESET}")
    print(f"2. {Colors.YELLOW}Show WiFi Info{Colors.RESET}")
    print(f"3. {Colors.BLUE}Scan Networks{Colors.RESET}")
    print(f"4. {Colors.RED}Exit{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description='WiFi Control Center')
    parser.add_argument('-f', '--force', action='store_true', 
                       help='Force restart without confirmation')
    args = parser.parse_args()
    
    if not check_termux_api():
        return
        
    if args.force:
        restart_wifi()
        return
    
    try:
        while True:
            clear_screen()
            print_banner()
            print_menu()
            
            choice = input(f"\n{Colors.BOLD}Choose an option (1-4):{Colors.RESET} ")
            
            if choice == '1':
                restart_wifi()
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '2':
                print_wifi_info()
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '3':
                networks = scan_networks()
                if networks:
                    print_networks(networks)
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '4':
                print(f"\n{Colors.GREEN}Goodbye!{Colors.RESET}")
                break
            else:
                print(f"\n{Colors.RED}Invalid option!{Colors.RESET}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.RESET}")

if __name__ == "__main__":
    main()
