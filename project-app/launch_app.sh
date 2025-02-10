#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# Find the correct Python version
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python is not installed."
    exit 1
fi

fuser -k 8050/tcp

echo "Iniciando el dashboard..."
$PYTHON "$SCRIPT_DIR/modulo_dashboard/app.py" &
DASHBOARD_PID=$!

wait $DASHBOARD_PID
