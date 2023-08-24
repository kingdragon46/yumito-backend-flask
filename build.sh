#!/bin/bash

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

# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies from requirements.txt
pip install -r "$PROJECT_DIR/requirements1.txt"

# Run the Flask application using Gunicorn
# gunicorn -w 4 -b 0.0.0.0:8000 app2:app2
