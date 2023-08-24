#!/bin/bash

# Set execute permission for this script
chmod +x "$0"

# Exit on error
set -o errexit

# Get the current directory (your Flask project directory)
PROJECT_DIR="$(pwd)"

# Check if 'requirements.txt' is present in the current directory
requirements_txt="$PROJECT_DIR/requirements.txt"

if [ ! -f "$requirements_txt" ]; then
    echo "Error: 'requirements.txt' not found in the current directory."
    exit 1
fi

# Create a virtual environment (if it doesn't already exist)
if [ ! -d "$PROJECT_DIR/venv" ]; then
    python -m venv "$PROJECT_DIR/venv"
fi

# Activate the virtual environment
source "$PROJECT_DIR/venv/bin/activate"

echo "Virtual environment activated."

# Upgrade pip
pip install --upgrade pip

# Install project dependencies from requirements.txt
pip install -r "$requirements_txt"

# Run the Flask application using Gunicorn
# Adjust the following line to match your Flask app's entry point
# gunicorn -w 4 -b 0.0.0.0:8000 app2:app2
