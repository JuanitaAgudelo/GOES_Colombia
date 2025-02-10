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

# Continue with the rest of the script
echo "Iniciando el módulo de procesamiento..."
$PYTHON "$SCRIPT_DIR/modulo_procesamiento/processing.py" &
PROCESAMIENTO_PID=$!

wait $DASHBOARD_PID
