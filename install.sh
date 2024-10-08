#!/bin/bash
set -e

echo "Starting custom installation script..."

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip



# If you have any specific packages that need special handling, install them here
# For example:
# echo "Installing specific package..."
# pip install some-package==1.2.3

# List installed packages
echo "Listing installed packages:"
pip list

echo "Custom installation script completed."

python -m ensurepip --upgrade
python -m pip install --upgrade setuptools