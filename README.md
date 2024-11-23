# Termux WiFi Restart Tool

A simple tool to restart your WiFi connection from Termux.

## Quick Installation

```bash
# Install git if you haven't already
pkg install git

# Clone the repository
git clone https://github.com/skiddato/termux-wifi-restart

# Go to the directory
cd termux-wifi-restart

# Run the installer
bash install.sh
```

After installation, simply run:
```bash
wifi-restart
```

Or force restart without confirmation:
```bash
wifi-restart -f
```

## Manual Installation

1. First, install the required packages in Termux:
```bash
pkg update
pkg install python termux-api
```

2. Copy the `wifi_restart.py` script to your Termux home directory:
```bash
cp wifi_restart.py ~
```

3. Make the script executable:
```bash
chmod +x ~/wifi_restart.py
```

## Features

- Shows current WiFi connection information
- Safely disables and re-enables WiFi
- Confirms successful reconnection
- Option to force restart without confirmation (-f flag)
- Checks for required Termux packages

## Troubleshooting

If you get a "Termux API not found" error:
1. Make sure you have the Termux:API app installed from the Play Store
2. Install the termux-api package: `pkg install termux-api`
3. Grant necessary permissions to Termux:API app in Android settings

## Notes

- Requires Termux and Termux:API app
- Requires Android permissions for WiFi control
- Some Android versions might restrict WiFi control capabilities

## License

MIT License - feel free to modify and distribute
