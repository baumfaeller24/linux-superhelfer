#!/bin/bash
"""
Development environment setup script for Linux Superhelfer.
"""

echo "Setting up Linux Superhelfer development environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Development environment setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To start all modules, run: python scripts/start_dev.py"