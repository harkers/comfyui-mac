#!/usr/bin/env bash
# ComfyUI Mac Toolkit — Installation script
# Idempotent: safe to re-run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMFYUI_HOME="${COMFYUI_HOME:-$HOME/comfyui-mac}"
VERIFIED_DIR="$HOME/.comfyui-mac"
PYTHON="${COMFYUI_HOME}/.venv/bin/python"

# ---- Helpers ---------------------------------------------------------------

info()  { printf "\033[32m[INFO]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[WARN]\033[0m %s\n" "$*" >&2; }
error() { printf "\033[31m[ERR]\033[0m %s\n" "$*" >&2; exit 1; }

# ---- Preflight -------------------------------------------------------------

info "Running preflight..."
if ! python3 -c "import torch; assert torch.backends.mps.is_available()"; then
    error "MPS not available. This toolkit requires Apple Silicon."
fi

# ---- Stage 0: ComfyUI base -------------------------------------------------

if [[ ! -d "$COMFYUI_HOME" ]]; then
    info "Cloning ComfyUI into $COMFYUI_HOME..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_HOME"
else
    info "ComfyUI already exists at $COMFYUI_HOME; pulling latest..."
    git -C "$COMFYUI_HOME" pull --ff-only || warn "Could not fast-forward ComfyUI"
fi

# ---- Virtualenv -------------------------------------------------------------

if [[ ! -d "$COMFYUI_HOME/.venv" ]]; then
    info "Creating virtualenv..."
    python3 -m venv "$COMFYUI_HOME/.venv"
fi

info "Installing/updating base dependencies..."
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install --upgrade -r "$COMFYUI_HOME/requirements.txt"

# ---- Custom nodes -----------------------------------------------------------

NODES_DIR="$COMFYUI_HOME/custom_nodes"
mkdir -p "$NODES_DIR"

while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and blank lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// /}" ]] && continue

    # Extract "owner/repo" from the last path segment
    repo_url="https://github.com/$line"
    repo_name="${line##*/}"
    target_dir="$NODES_DIR/$repo_name"

    if [[ -d "$target_dir" ]]; then
        info "Updating $repo_name..."
        git -C "$target_dir" pull --ff-only || warn "Could not update $repo_name"
    else
        info "Installing $repo_name..."
        git clone "$repo_url" "$target_dir"
    fi

    # Install node-specific requirements if present
    if [[ -f "$target_dir/requirements.txt" ]]; then
        info "Installing requirements for $repo_name..."
        "$PYTHON" -m pip install --upgrade -r "$target_dir/requirements.txt"
    fi
done < "$SCRIPT_DIR/custom_nodes.txt"

# ---- Verified flag directory ------------------------------------------------

mkdir -p "$VERIFIED_DIR"

info "Stage 0 complete."
info "Next steps:"
info "  1. ./pull_models.sh"
info "  2. ./stage1_verify.py"
