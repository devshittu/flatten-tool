#!/bin/bash

# Uninstall flatten tool (pipx, local, or global)
set -e

# Define paths
GLOBAL_INSTALL_DIR="/usr/local/bin"
GLOBAL_SCRIPT_NAME="flatten"
GLOBAL_PLUGIN_DIR="/usr/local/share/flatten/plugins"
GLOBAL_TEMPLATE_DIR="/usr/local/share/flatten/templates"
LOCAL_VENV_DIR=".venv"

# Dependencies
DEPENDENCIES="tqdm colorama jsonschema pytest flattenify"

# Parse arguments
UNINSTALL_MODE="pipx"
while [[ $# -gt 0 ]]; do
    case $1 in
        --pipx)
            UNINSTALL_MODE="pipx"
            shift
            ;;
        --local)
            UNINSTALL_MODE="local"
            shift
            ;;
        --global)
            UNINSTALL_MODE="global"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--pipx|--local|--global]"
            exit 1
            ;;
    esac
done

if [ "$UNINSTALL_MODE" = "pipx" ]; then
    echo "Uninstalling flattenify via pipx..."

    # Check for pipx
    if ! command -v pipx &>/dev/null; then
        echo "pipx not found. Assuming flattenify was not installed via pipx."
        exit 0
    fi

    # Uninstall flattenify
    pipx uninstall flattenify || true

    echo "Pipx uninstallation successful."

elif [ "$UNINSTALL_MODE" = "local" ]; then
    echo "Uninstalling local flattenify..."

    # Remove virtual environment
    if [ -d "$LOCAL_VENV_DIR" ]; then
        echo "Removing virtual environment: $LOCAL_VENV_DIR..."
        rm -rf "$LOCAL_VENV_DIR"
    else
        echo "Warning: Virtual environment not found."
    fi

    echo "Local uninstallation successful."

else
    echo "Uninstalling global flattenify..."

    # Remove script
    if [ -f "$GLOBAL_INSTALL_DIR/$GLOBAL_SCRIPT_NAME" ]; then
        echo "Removing $GLOBAL_SCRIPT_NAME from $GLOBAL_INSTALL_DIR..."
        sudo rm "$GLOBAL_INSTALL_DIR/$GLOBAL_SCRIPT_NAME"
    else
        echo "Warning: $GLOBAL_SCRIPT_NAME not found in $GLOBAL_INSTALL_DIR."
    fi

    # Remove plugins and templates
    if [ -d "$GLOBAL_PLUGIN_DIR" ]; then
        echo "Removing $GLOBAL_PLUGIN_DIR..."
        sudo rm -rf "$GLOBAL_PLUGIN_DIR"
    fi
    if [ -d "$GLOBAL_TEMPLATE_DIR" ]; then
        echo "Removing $GLOBAL_TEMPLATE_DIR..."
        sudo rm -rf "$GLOBAL_TEMPLATE_DIR"
    fi

    # Uninstall dependencies
    echo "Uninstalling dependencies: $DEPENDENCIES..."
    pip3 uninstall -y $DEPENDENCIES 2>/dev/null || true

    echo "Global uninstallation successful."
fi

# File path: ./uninstall.sh
