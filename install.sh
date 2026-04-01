#!/bin/bash
# install.sh — Run this once to install the Countdown Timer on Ubuntu 24.04

set -e

echo "=== Installing Countdown Timer ==="

# 1. Ensure tkinter is installed
echo "[1/4] Checking Python tkinter..."
sudo apt-get install -y python3-tk 2>/dev/null && echo "  ✓ tkinter ready"

# 2. Copy app to /opt
echo "[2/4] Copying app files..."
sudo mkdir -p /opt/countdown_timer
sudo cp countdown.py /opt/countdown_timer/countdown.py
sudo chmod +x /opt/countdown_timer/countdown.py
echo "  ✓ App installed to /opt/countdown_timer/"

# 3. Install desktop entry
echo "[3/4] Installing desktop entry..."
cp countdown-timer.desktop ~/.local/share/applications/countdown-timer.desktop
# Update Exec path in desktop file
sed -i "s|/opt/countdown_timer/countdown.py|/opt/countdown_timer/countdown.py|g" \
    ~/.local/share/applications/countdown-timer.desktop
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
echo "  ✓ App added to application launcher"

# 4. Create a quick-launch alias
echo "[4/4] Adding shell alias 'countdown'..."
ALIAS_LINE="alias countdown='python3 /opt/countdown_timer/countdown.py &'"
SHELL_RC="$HOME/.bashrc"
if ! grep -q "alias countdown=" "$SHELL_RC"; then
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "  ✓ Alias added to $SHELL_RC"
else
    echo "  ✓ Alias already exists"
fi

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Launch options:"
echo "  1. Terminal:  python3 /opt/countdown_timer/countdown.py"
echo "  2. After 'source ~/.bashrc':  countdown"
echo "  3. App Grid:  Search 'Countdown Timer'"
echo ""
