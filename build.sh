#!/bin/bash

# Set execute permission for this script
chmod +x "$0"

# Step 1: Update and upgrade packages using sudo
echo "Step 1: Updating and upgrading packages..."
sudo apt-get update
sudo apt-get upgrade -y
echo "Step 1 complete."

# Step 2: Reboot the server to address read-only filesystem issues
echo "Step 2: Rebooting the server..."
sudo reboot

# Set execute permission for the script itself
chmod +x "$0"

# Update Python (assuming you're using apt-get)
apt-get update
apt-get install --only-upgrade python3

# exit on error
set -o errexit

# Get the current directory (your Flask project directory)
PROJECT_DIR="$(pwd)"

# Create a virtual environment (if it doesn't already exist)
if [ ! -d "$PROJECT_DIR/venv" ]; then
   python -m venv "$PROJECT_DIR/venv"
fi

# Activate the virtual environment
source "$PROJECT_DIR/venv/bin/activate"

echo "Env activated"

# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies from requirements.txt
pip install -r requirements.txt

# Run the Flask application using Gunicorn
# gunicorn -w 4 -b 0.0.0.0:8000 app2:app2
