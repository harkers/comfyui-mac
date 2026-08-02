# ComfyUI Mac Toolkit

> Apple Silicon-native ComfyUI management, preflight checks, and render automation.

## Setup

### Prerequisites
- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.12+ and `uv`

### Installation

```bash
# Install dependencies
make install

# Run the installer (idempotent)
./install.sh

# Pull models (~25GB)
./pull_models.sh

# Verify Stage 1
./stage1_verify.py
```

## Usage

```bash
# Render a workflow
uv run python render.py run workflows/01_videohelpersuite_pass.json

# Check preflight status
uv run python -c "from lib.preflight import run_preflight; run_preflight()"
```

## Development Commands

```bash
# Run full test suite
make test

# Run individual test files
make test-preflight
make test-memcheck
make test-api
make test-cli
make test-stage1

# Lint and format
make lint
make format

# Mark a task as done in todo.md
make todo TASK=2
```

## Project Structure

| Path | Purpose |
|---|---|
| `lib/` | Python library code |
| `tests/` | pytest suite |
| `workflows/` | API-exported workflow JSONs |
| `scripts/` | Automation (todo updater, etc.) |
| `render.py` | CLI entry point |
| `install.sh` | Full ComfyUI + node setup |
| `pull_models.sh` | Resumable HF model downloads |
| `stage1_verify.py` | Post-install verification |

## ComfyUI Context

- **Backend:** MPS (not CUDA)
- **Custom nodes:** 6 packs (see `custom_nodes.txt`)
- **Dropped nodes:** LTX-Video, WanVideoWrapper (no MPS path)
- **Model downloads:** ~25GB from HuggingFace

## License

MIT
