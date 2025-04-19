#!/bin/bash

# Install flatten tool system-wide
set -e

# Define paths
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="flatten"
PYTHON_SCRIPT="flatten/cli.py"
PLUGIN_DIR="/usr/local/share/flatten/plugins"
TEMPLATE_DIR="/usr/local/share/flatten/templates"

# Check for Python3
if ! command -v python3 &>/dev/null; then
    echo "Error: Python3 is required but not installed."
    exit 1
fi

# Check Python version (minimum 3.8 for 2024 best practices)
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "Error: Python 3.8 or higher is required."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user tqdm colorama jsonschema pytest

# Create plugin and template directories
sudo mkdir -p "$PLUGIN_DIR" "$TEMPLATE_DIR"
sudo chmod 755 "$PLUGIN_DIR" "$TEMPLATE_DIR"

# Copy Python script and plugins
echo "Installing $SCRIPT_NAME to $INSTALL_DIR..."
sudo cp "$PYTHON_SCRIPT" "$INSTALL_DIR/$SCRIPT_NAME"
sudo chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
sudo cp -r plugins/* "$PLUGIN_DIR" 2>/dev/null || true
sudo cp -r templates/* "$TEMPLATE_DIR" 2>/dev/null || true

# Verify installation
if command -v flatten &>/dev/null; then
    echo "Installation successful! Run 'flatten --help' for usage."
else
    echo "Installation failed."
    exit 1
fi

# Snap packaging instructions
echo "To package as a Snap, create a snapcraft.yaml with the following base:"
cat << EOF
name: flatten
version: '1.0'
summary: Flatten project files into a single file
description: A CLI tool to flatten code files with descriptive paths.
base: core22
confinement: strict
parts:
  flatten:
    plugin: python
    source: .
    python-packages:
      - tqdm
      - colorama
      - jsonschema
      - pytest
apps:
  flatten:
    command: bin/flatten
EOF
echo "Run 'snapcraft' to build the Snap package."