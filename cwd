#!/bin/zsh
# cwd - Cell War Driver command-line wrapper

# Get the directory of this script
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || { echo "Error: Failed to change to script directory"; exit 1; }

# Execute the main program with all arguments passed
python -B main.py "$@"
