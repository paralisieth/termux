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

def print_status(wifi_info):
    """Print current WiFi status with nice formatting"""
    if wifi_info:
        ssid = wifi_info.get('ssid', 'Unknown')
        rssi = wifi_info.get('rssi', 0)
        ip = wifi_info.get('ip', 'Unknown')
        
        # Calculate signal strength
        if rssi >= -50:
            signal = f"{Colors.GREEN}Excellent{Colors.RESET}"
        elif rssi >= -60:
            signal = f"{Colors.GREEN}Good{Colors.RESET}"
        elif rssi >= -70:
            signal = f"{Colors.YELLOW}Fair{Colors.RESET}"
        else:
            signal = f"{Colors.RED}Poor{Colors.RESET}"
        
        print(f"\n{Colors.BOLD}Current Connection:{Colors.RESET}")
        print(f"├─ Network: {Colors.GREEN}{ssid}{Colors.RESET}")
        print(f"├─ Signal:  {signal} ({rssi} dBm)")
        print(f"└─ IP:      {Colors.BLUE}{ip}{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}Not connected to any WiFi network{Colors.RESET}")

def print_menu():
    """Print interactive menu"""
    print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
    print(f"1. {Colors.GREEN}Restart WiFi{Colors.RESET}")
    print(f"2. {Colors.YELLOW}Show WiFi Info{Colors.RESET}")
    print(f"3. {Colors.BLUE}Monitor Signal{Colors.RESET}")
    print(f"4. {Colors.RED}Exit{Colors.RESET}")

def check_termux_packages():
    """Check if required Termux API packages are installed"""
    try:
        subprocess.run(['termux-wifi-connectioninfo'], capture_output=True)
        return True
    except FileNotFoundError:
        print(f"\n{Colors.RED}⚠️ Termux API not found!{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please install required packages with:{Colors.RESET}")
        print(f"{Colors.GREEN}pkg install termux-api{Colors.RESET}")
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

def monitor_signal():
    """Monitor WiFi signal strength in real-time"""
    try:
        while True:
            clear_screen()
            print_banner()
            wifi_info = get_wifi_info()
            if wifi_info:
                rssi = wifi_info.get('rssi', 0)
                ssid = wifi_info.get('ssid', 'Unknown')
                
                # Create signal bar
                signal_strength = abs(rssi)
                bars = max(0, min(5, int((100 - signal_strength) / 20)))
                bar = '█' * bars + '░' * (5 - bars)
                
                print(f"\n{Colors.BOLD}Signal Monitor for: {Colors.GREEN}{ssid}{Colors.RESET}")
                print(f"\nSignal Strength: {bar} {rssi} dBm")
                print(f"\nPress Ctrl+C to return to menu")
                
                time.sleep(1)
            else:
                print(f"\n{Colors.RED}Not connected to WiFi{Colors.RESET}")
                break
    except KeyboardInterrupt:
        return

def restart_wifi():
    """Restart WiFi connection with progress animation"""
    print(f"\n{Colors.YELLOW}📱 Restarting WiFi...{Colors.RESET}")
    
    # Disable WiFi
    print(f"\n{Colors.RED}→ Disabling WiFi...{Colors.RESET}")
    subprocess.run(['termux-wifi-enable', 'false'])
    time.sleep(2)
    
    # Enable WiFi with loading animation
    print(f"\n{Colors.GREEN}→ Enabling WiFi...{Colors.RESET}")
    subprocess.run(['termux-wifi-enable', 'true'])
    
    # Wait for connection with animation
    animation = "|/-\\"
    for i in range(10):
        print(f"\r{Colors.CYAN}Waiting for connection... {animation[i % len(animation)]}{Colors.RESET}", end='')
        time.sleep(0.5)
    print()
    
    # Check new connection
    new_info = get_wifi_info()
    if new_info and new_info.get('ssid'):
        print(f"\n{Colors.GREEN}✅ Successfully reconnected to: {new_info['ssid']}{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ Failed to reconnect to WiFi{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description='Restart WiFi connection in Termux')
    parser.add_argument('-f', '--force', action='store_true', 
                       help='Force restart without confirmation')
    args = parser.parse_args()
    
    if not check_termux_packages():
        return
        
    if args.force:
        restart_wifi()
        return
    
    try:
        while True:
            clear_screen()
            print_banner()
            
            wifi_info = get_wifi_info()
            print_status(wifi_info)
            print_menu()
            
            choice = input(f"\n{Colors.BOLD}Choose an option (1-4):{Colors.RESET} ")
            
            if choice == '1':
                restart_wifi()
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '2':
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == '3':
                monitor_signal()
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
