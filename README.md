# ComfyUI Mac Toolkit

> Apple Silicon-native ComfyUI management, preflight checks, and render automation.

## What This Is

A CLI toolkit that manages a local ComfyUI installation on Apple Silicon Macs. It handles preflight checks, workflow rendering, model downloads, and post-install verification — all via a single Python project with no manual UI clicking.

**Hardware target:** Apple Silicon (M1/M2/M3/M4) using the **MPS** backend. CUDA is not supported.

## Quick Start

```bash
# 1. Install dependencies
make install

# 2. Run the idempotent installer
./install.sh

# 3. Download models (~25GB)
./pull_models.sh

# 4. Verify Stage 1
./stage1_verify.py

# 5. Render a workflow
uv run python render.py run workflows/01_videohelpersuite_pass.json
```

## Prerequisites

- macOS on Apple Silicon
- Python 3.12+ and `uv`
- ~30GB free disk space (ComfyUI + models)

## Installation

The toolkit installs ComfyUI to `~/comfyui-mac` (configurable via `$COMFYUI_HOME`). This is **not** inside the repo — it's a runtime directory.

```bash
./install.sh
```

This script:
1. Clones/updates ComfyUI into `~/comfyui-mac`
2. Creates a virtualenv
3. Installs/updates base dependencies
4. Installs 6 custom node packs (see below)
5. Installs per-node requirements when present
6. Creates `~/.comfyui-mac/` for the verified flag

### Known Issue: `decord` on Apple Silicon

`ComfyUI-LatentSyncWrapper` depends on `decord`, which has no prebuilt wheel for Python 3.14 + macOS ARM64. If you hit this error:

```bash
# Option A: Build from source
cd ~/comfyui-mac
source .venv/bin/activate
pip install --upgrade --force-reinstall git+https://github.com/dmlc/decord.git

# Option B: Use the eva-decord fork
pip install eva-decord
```

If both fail, LatentSyncWrapper will fall back to `opencv-python` for video I/O.

## Model Downloads

Models are pulled from HuggingFace and stored in `~/comfyui-mac/models/`.

| Model | Repo | Size | Destination |
|---|---|---|---|
| LatentSync UNet | `ByteDance/LatentSync` | ~300MB | `checkpoints/` |
| HunyuanVideo-GGUF | `city96/HunyuanVideo-gguf` | ~8GB | `checkpoints/` |
| VEnhancer | `Kijai/VEnhancer-fp16` | ~5GB | `checkpoints/` |
| RIFE | `imaginairy/rife-interpolation` | ~100MB | `checkpoints/` |

Run `./pull_models.sh` to download. It's resumable — already-downloaded files are skipped.

## Custom Nodes

| # | Node Pack | GitHub Repo | MPS Status |
|---|-----------|-------------|------------|
| 1 | VideoHelperSuite | `Kosinkadink/ComfyUI-VideoHelperSuite` | ✅ Native |
| 2 | ComfyUI-GGUF | `city96/ComfyUI-GGUF` | ✅ Native |
| 3 | HunyuanVideoWrapper | `kijai/ComfyUI-HunyuanVideoWrapper` | ✅ Native |
| 4 | LatentSyncWrapper | `ShmuelRonen/ComfyUI-LatentSyncWrapper` | ⚠️ Needs `decord` fix |
| 5 | Frame-Interpolation | `Fannovel16/ComfyUI-Frame-Interpolation` | ✅ Native |
| 6 | VEnhancer | `kijai/ComfyUI-VEnhancer` | ✅ Native |

### Dropped Nodes

These packs have **no native MPS path** and are excluded:
- **LTX-Video** — requires CUDA kernels
- **WanVideoWrapper** — requires CUDA kernels

## Usage

### Render a Workflow

```bash
# Basic render
uv run python render.py run workflows/01_videohelpersuite_pass.json

# Custom ComfyUI URL
uv run python render.py run workflows/02_gguf_pass.json --url http://localhost:8188

# Custom timeout (default 300s)
uv run python render.py run workflows/03_hunyuanvideowrapper_pass.json --timeout 600
```

### Check Preflight

```bash
uv run python -c "from lib.preflight import run_preflight; print(run_preflight())"
```

### Check Memory

```bash
uv run python -c "from lib.memcheck import memory_warning; print(memory_warning())"
```

## CLI Exit Codes

`render.py` uses the following exit codes:

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Workflow rendered and outputs fetched |
| 1 | Not verified / config drifted | Preflight failed (missing verified flag or MPS unavailable) |
| 2 | ComfyUI not running | Connection refused on submit |
| 3 | Failed after starting | Job error or unexpected submit failure |
| 4 | Timeout | Job didn't complete within `--timeout` |

## Development

### Run Tests

```bash
# Full suite
make test

# Individual modules
make test-preflight
make test-memcheck
make test-api
make test-cli
make test-stage1
```

### Lint & Format

```bash
make lint
make format
```

### Update Todo After a Task

```bash
make todo TASK=2
```

## Project Structure

| Path | Purpose |
|---|---|
| `lib/preflight.py` | Environment checks (MPS, verified flag) |
| `lib/memcheck.py` | System memory monitoring |
| `lib/api.py` | ComfyClient + retry logic |
| `render.py` | CLI entry point |
| `install.sh` | Idempotent ComfyUI + node installer |
| `pull_models.sh` | Resumable HF model downloads |
| `stage1_verify.py` | Post-install verification |
| `tests/` | pytest suite (33 tests) |
| `workflows/` | API-exported workflow JSONs (MVR) |
| `custom_nodes.txt` | Node pack roster |
| `models.sha256` | Downloaded model checksums |

## Security

- This toolkit **does not** expose ComfyUI to the public internet. ComfyUI runs on `127.0.0.1:8188` by default.
- Do not expose port 8188 externally without authentication — ComfyUI has no built-in auth.
- Model files are verified via SHA-256 after download (see `models.sha256`).

## License

MIT
