#!/bin/bash

# Set execute permission for this script
chmod +x "$0"

# Update Python (assuming you're using apt-get)
# sudo apt-get update  # This line requires root access
# sudo apt-get install --only-upgrade python3  # This line requires root access

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
