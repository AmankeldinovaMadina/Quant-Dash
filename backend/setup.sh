#!/bin/bash

# Setup script for Quant-Dash backend
# This script creates a virtual environment and installs all dependencies

echo "🚀 Setting up Quant-Dash Backend Environment"
echo "=============================================="

# Check if we're already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "⚠️  You're already in a virtual environment: $VIRTUAL_ENV"
    echo "   Please deactivate it first with: deactivate"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o 'Python [0-9]\+\.[0-9]\+' | grep -o '[0-9]\+\.[0-9]\+')
echo "🐍 Detected Python version: $PYTHON_VERSION"

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip to latest version
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"
python -c "import aiohttp; print(f'aiohttp version: {aiohttp.__version__}')"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To activate the environment in the future, run:"
echo "   source venv/bin/activate"
echo ""
echo "To test the Finnhub integration, run:"
echo "   python test_simple.py"
echo "   python test_finnhub.py"
