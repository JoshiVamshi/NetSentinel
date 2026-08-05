#!/bin/bash
# NetSentinel Linux Service Installer

set -e

echo "======================================"
echo "NetSentinel Service Installer"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Configuration
INSTALL_DIR="/opt/netsentinel"
SERVICE_FILE="netsentinel.service"
SERVICE_USER="netsentinel"

echo "📦 Installing NetSentinel..."

# Create user if doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating user: $SERVICE_USER"
    useradd -r -s /bin/false $SERVICE_USER
fi

# Create installation directory
echo "Creating directory: $INSTALL_DIR"
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/logs

# Copy files
echo "Copying files..."
cp -r ../* $INSTALL_DIR/
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r $INSTALL_DIR/requirements.txt

# Install systemd service
echo "Installing systemd service..."
cp $SERVICE_FILE /etc/systemd/system/
systemctl daemon-reload

# Enable and start service
echo "Enabling service..."
systemctl enable netsentinel.service

echo ""
echo "✅ Installation complete!"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start netsentinel"
echo "  Stop:    sudo systemctl stop netsentinel"
echo "  Status:  sudo systemctl status netsentinel"
echo "  Logs:    sudo journalctl -u netsentinel -f"
echo ""
echo "Dashboard: http://localhost:5000"
echo ""
