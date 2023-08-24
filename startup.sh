#!/bin/bash

# Set execute permission for this script
chmod +x "$0"

# Exit on error
set -o errexit

# Get the current directory (your Flask project directory)
PROJECT_DIR="$(pwd)"

# Navigate to your Flask project directory
cd "$PROJECT_DIR" || exit 1

# Activate the virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Run the Flask application using Gunicorn
# Adjust the following line to match your Flask app's entry point
gunicorn -w 4 -b 0.0.0.0:8000 app:app
