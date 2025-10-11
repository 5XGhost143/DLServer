#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Please run the Script with sudo."
    exit 1
fi

VENV_DIR="DLServer"


if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual Environment doesn't exist. creating it now..."
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    echo "installing packages..."
    pip install -r requirements.txt
else
    echo "Virtual Environment already exists. activating it..."
    source $VENV_DIR/bin/activate
fi

echo "Starting main.py..."
python main.py

