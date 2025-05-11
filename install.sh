#!/bin/bash

# Install flatten tool via pipx (recommended), locally, or globally
set -e

# Define paths
GLOBAL_INSTALL_DIR="/usr/local/bin"
GLOBAL_SCRIPT_NAME="flatten"
GLOBAL_PLUGIN_DIR="/usr/local/share/flatten/plugins"
GLOBAL_TEMPLATE_DIR="/usr/local/share/flatten/templates"
LOCAL_VENV_DIR=".venv"
PYTHON_SCRIPT="src/flatten_tool/flatten/cli.py"

# Dependencies
DEPENDENCIES="tqdm==4.66.5 colorama==0.4.6 jsonschema==4.23.0 pytest==8.3.3"

# Check for Python3
if ! command -v python3 &>/dev/null; then
    echo "Error: Python3 is required but not installed."
    exit 1
fi

# Check Python version (minimum 3.8)
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "Error: Python 3.8 or higher is required."
    exit 1
fi

# Parse arguments
INSTALL_MODE="pipx"
while [[ $# -gt 0 ]]; do
    case $1 in
        --pipx)
            INSTALL_MODE="pipx"
            shift
            ;;
        --local)
            INSTALL_MODE="local"
            shift
            ;;
        --global)
            INSTALL_MODE="global"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--pipx|--local|--global]"
            exit 1
            ;;
    esac
done

if [ "$INSTALL_MODE" = "pipx" ]; then
    echo "Installing flattenify via pipx (recommended)..."

    # Check for pipx
    if ! command -v pipx &>/dev/null; then
        echo "pipx not found. Installing pipx..."
        pip3 install --user pipx
        export PATH="$HOME/.local/bin:$PATH"
    fi

    # Install flattenify
    echo "Installing flattenify via pipx..."
    pipx install .

    # Verify installation
    if command -v flatten &>/dev/null; then
        echo "Pipx installation successful! Run 'flatten --help' for usage."
        echo "If 'flatten' is not found, run 'pipx ensurepath' and restart your terminal."
    else
        echo "Pipx installation failed."
        exit 1
    fi

elif [ "$INSTALL_MODE" = "local" ]; then
    echo "Installing flattenify locally in a virtual environment..."

    # Create virtual environment
    python3 -m venv $LOCAL_VENV_DIR
    source $LOCAL_VENV_DIR/bin/activate

    # Install dependencies
    echo "Installing dependencies: $DEPENDENCIES..."
    pip install $DEPENDENCIES
    pip install -e .

    # Copy plugins and templates locally
    mkdir -p src/flatten_tool/plugins src/flatten_tool/templates
    cp -r src/flatten_tool/plugins/* src/flatten_tool/plugins/ 2>/dev/null || true
    cp -r src/flatten_tool/templates/* src/flatten_tool/templates/ 2>/dev/null || true

    deactivate

    echo "Local installation successful!"
    echo "Activate the virtual environment: source $LOCAL_VENV_DIR/bin/activate"
    echo "Run the tool with: flatten <command> or python -m flatten_tool.flatten.cli <command>"
    echo "Example: flatten init or python -m flatten_tool.flatten.cli init"

else
    echo "Installing flattenify globally..."

    # Check for dependency conflicts
    echo "Checking for dependency conflicts..."
    CONFLICTS=$(pip list --format=json | python3 -c "import json, sys; installed = {p['name']: p['version'] for p in json.load(sys.stdin)}; conflicts = []; reqs = '$DEPENDENCIES'.split(); [conflicts.append(f'{req.split('==')[0]}: installed {installed.get(req.split('==')[0], 'not installed')}, required {req}') for req in reqs if req.split('==')[0] in installed and installed[req.split('==')[0]] != req.split('==')[1]]; print('\n'.join(conflicts))")
    if [ -n "$CONFLICTS" ]; then
        echo "Warning: Dependency conflicts detected:"
        echo "$CONFLICTS"
        read -p "Proceed with installation? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation aborted."
            exit 1
        fi
    fi

    # Install dependencies and package
    echo "Installing dependencies: $DEPENDENCIES..."
    pip3 install --user $DEPENDENCIES
    pip3 install --user .

    # Create global directories
    sudo mkdir -p "$GLOBAL_PLUGIN_DIR" "$GLOBAL_TEMPLATE_DIR"
    sudo chmod 755 "$GLOBAL_PLUGIN_DIR" "$GLOBAL_TEMPLATE_DIR"

    # Copy plugins and templates
    sudo cp -r src/flatten_tool/plugins/* "$GLOBAL_PLUGIN_DIR" 2>/dev/null || true
    sudo cp -r src/flatten_tool/templates/* "$GLOBAL_TEMPLATE_DIR" 2>/dev/null || true

    # Verify installation
    if command -v flatten &>/dev/null; then
        echo "Global installation successful! Run 'flatten --help' for usage."
    else
        echo "Installation failed."
        exit 1
    fi
fi

# File path: ./install.sh
