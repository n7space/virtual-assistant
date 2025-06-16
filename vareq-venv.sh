#!/bin/bash

VENV_DIR="./venv"

# Determine which Python command is available
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "Error: No Python interpreter found"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please install the application in a virtual environment by invoking make install-venv"
    exit 1
fi

source "$VENV_DIR/bin/activate" || source "$VENV_DIR/Scripts/activate"

${PYTHON} -m vareq.vareq "$@"

deactivate