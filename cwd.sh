#!/bin/zsh
# cwd - Cell War Driver command-line wrapper

# Get the directory of this script
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || { echo "Error: Failed to change to script directory"; exit 1; }

# Check if virtual environment exists, create it if it doesn't
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv || { echo "Error: Failed to create virtual environment"; exit 1; }
fi

# Activate virtual environment
source .venv/bin/activate || { echo "Error: Failed to activate virtual environment"; exit 1; }

# Install requirements if they don't exist
if [ ! -f ".venv/lib/python3*/site-packages/pyserial*" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt || { echo "Error: Failed to install dependencies"; exit 1; }
fi

# Execute the main program with all arguments passed
python -B main.py "$@"
