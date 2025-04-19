#!/bin/bash

# Uninstall flatten tool
set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="flatten"
PLUGIN_DIR="/usr/local/share/flatten/plugins"
TEMPLATE_DIR="/usr/local/share/flatten/templates"

# Remove script
if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo "Removing $SCRIPT_NAME from $INSTALL_DIR..."
    sudo rm "$INSTALL_DIR/$SCRIPT_NAME"
else
    echo "Warning: $SCRIPT_NAME not found in $INSTALL_DIR."
fi

# Remove plugins and templates
if [ -d "$PLUGIN_DIR" ]; then
    echo "Removing $PLUGIN_DIR..."
    sudo rm -rf "$PLUGIN_DIR"
fi
if [ -d "$TEMPLATE_DIR" ]; then
    echo "Removing $TEMPLATE_DIR..."
    sudo rm -rf "$TEMPLATE_DIR"
fi

echo "Uninstallation successful."