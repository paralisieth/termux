#!/data/data/com.termux/files/usr/bin/bash

echo "Installing Termux WiFi Restart Tool..."

# Update package list
pkg update -y

# Install required packages
pkg install -y python termux-api

# Copy script to user's bin directory
cp wifi_restart.py $PREFIX/bin/wifi-restart

# Make it executable
chmod +x $PREFIX/bin/wifi-restart

echo "✅ Installation complete!"
echo "You can now use the command: wifi-restart"
