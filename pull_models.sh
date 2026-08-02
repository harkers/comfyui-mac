#!/usr/bin/env bash
# ComfyUI Mac Toolkit — Model downloader
# Resumable HuggingFace downloads with SHA-256 verification.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMFYUI_HOME="${COMFYUI_HOME:-$HOME/comfyui-mac}"
MODELS_DIR="$COMFYUI_HOME/models"

# ---- Configuration ----------------------------------------------------------

# Each entry is 3 consecutive array elements: repo_id, filename, subdir
MODELS=(
    "ByteDance/LatentSync"
    "latentsync_unet.pt"
    "checkpoints"

    "city96/HunyuanVideo-gguf"
    "hunyuan-video-t2v-720p-Q4_K_M.gguf"
    "checkpoints"

    "Kijai/VEnhancer-fp16"
    "venhancer_v2-fp16.safetensors"
    "checkpoints"

    "imaginairy/rife-interpolation"
    "rife-flownet-4.13.2.safetensors"
    "checkpoints"
)

SHA256_FILE="$SCRIPT_DIR/models.sha256"

# ---- Helpers ---------------------------------------------------------------

info()  { printf "\033[32m[INFO]\033[0m %s\n" "$*"; }
warn()  { printf "\033[33m[WARN]\033[0m %s\n" "$*" >&2; }
error() { printf "\033[31m[ERR]\033[0m %s\n" "$*" >&2; exit 1; }

# ---- Pull -------------------------------------------------------------------

mkdir -p "$MODELS_DIR"

# Ensure huggingface_hub is available
if ! python3 -c "import huggingface_hub" 2>/dev/null; then
    info "Installing huggingface_hub..."
    pip install huggingface_hub
fi

i=0
while [ $i -lt ${#MODELS[@]} ]; do
    repo_id="${MODELS[$i]}"
    filename="${MODELS[$((i+1))]}"
    subdir="${MODELS[$((i+2))]}"
    i=$((i+3))

    target_dir="$MODELS_DIR/$subdir"
    target_path="$target_dir/$filename"

    mkdir -p "$target_dir"

    if [[ -f "$target_path" ]]; then
        info "$filename already exists; skipping download."
    else
        info "Downloading $filename from $repo_id..."
        python3 -c "
from huggingface_hub import hf_hub_download
import sys
try:
    hf_hub_download(
        repo_id='${repo_id}',
        filename='${filename}',
        local_dir='${target_dir}',
        local_dir_use_symlinks=False,
    )
except Exception as e:
    print(f'Download failed: {e}', file=sys.stderr)
    sys.exit(1)
"
    fi

    # Record checksum
    if command -v sha256sum >/dev/null 2>&1; then
        hash=$(sha256sum "$target_path" | awk '{print $1}')
    else
        hash=$(shasum -a 256 "$target_path" | awk '{print $1}')
    fi
    echo "$hash  $subdir/$filename" >> "$SHA256_FILE.tmp"
done

# ---- Finalise checksums ------------------------------------------------------

# Deduplicate and sort
if [[ -f "$SHA256_FILE.tmp" ]]; then
    sort -u "$SHA256_FILE.tmp" > "$SHA256_FILE"
    rm "$SHA256_FILE.tmp"
    info "Updated $SHA256_FILE"
fi

info "Model downloads complete."
