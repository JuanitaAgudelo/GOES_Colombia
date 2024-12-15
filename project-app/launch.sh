#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# Activate the virtual environment using a relative path
source "$SCRIPT_DIR/venv/bin/activate"

# Continue with the rest of the script
echo "Iniciando el módulo de procesamiento..."
python "$SCRIPT_DIR/modulo_procesamiento/processing.py" &
PROCESAMIENTO_PID=$!

sleep 49

echo "Iniciando el dashboard..."
python "$SCRIPT_DIR/modulo_dashboard/app.py" &
DASHBOARD_PID=$!

wait $PROCESAMIENTO_PID $DASHBOARD_PID
