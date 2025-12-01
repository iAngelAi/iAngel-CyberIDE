#!/bin/bash

# CyberIDE Neural Core - Installation Script
# This script installs all dependencies and validates the installation

set -e  # Exit on error

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║      🧠 CyberIDE Neural Core Installation 🧠              ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    echo "   Install Python 3.10 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "   Please run this script from the CyberIDE project root"
    exit 1
fi

echo "✓ Found requirements.txt"

# Create virtual environment (optional but recommended)
read -p "Create a virtual environment? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Creating virtual environment..."
    if [ -d "venv" ]; then
        echo "⚠ Virtual environment already exists"
        read -p "Remove and recreate? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            echo "✓ Virtual environment created"
        fi
    else
        python3 -m venv venv
        echo "✓ Virtual environment created"
    fi

    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source venv/bin/activate"
    echo ""
    read -p "Activate now and continue? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        source venv/bin/activate
        echo "✓ Virtual environment activated"
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes..."
echo ""

pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ All dependencies installed successfully"
else
    echo ""
    echo "❌ Error installing dependencies"
    exit 1
fi

# Validate installation
echo ""
echo "Validating installation..."
echo ""

python3 validate_neural_core.py

if [ $? -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║              ✓ Installation Complete! ✓                  ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Start the Neural Core:"
    echo "   python3 start_neural_core.py"
    echo ""
    echo "2. In another terminal, start the React frontend:"
    echo "   npm run dev"
    echo ""
    echo "3. Open your browser to http://localhost:5173"
    echo ""
    echo "For more information, see:"
    echo "  - NEURAL_CORE_GUIDE.md (complete guide)"
    echo "  - neural_cli/README.md (API documentation)"
    echo ""
else
    echo ""
    echo "❌ Installation validation failed"
    echo "   Please check the errors above and try again"
    exit 1
fi
