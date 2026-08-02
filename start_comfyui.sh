#!/usr/bin/env bash
# Start ComfyUI on Apple Silicon with MPS backend

set -euo pipefail

COMFYUI_HOME="${COMFYUI_HOME:-$HOME/comfyui-mac}"
VENV="$COMFYUI_HOME/.venv/bin/activate"

if [[ ! -f "$VENV" ]]; then
    echo "Virtualenv not found at $VENV"
    echo "Run ./install.sh first"
    exit 1
fi

# Activate virtualenv
source "$VENV"

cd "$COMFYUI_HOME"

# Run ComfyUI on localhost with MPS
exec python main.py --listen 127.0.0.1 --port 8190
