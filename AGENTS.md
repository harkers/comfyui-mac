# AGENTS.md — comfyui-mac

> High-signal context for OpenCode sessions. Everything here answers: "Would an agent likely miss this without help?"

## Repo state

**Active development.** Tasks 1–8 complete (scaffold, preflight, memcheck, api, render, install, pull_models, stage1_verify). Tasks 9–11 (MVR workflows, final README, real hardware verification) are pending and require a live ComfyUI UI. The canonical implementation plan lives in `todo.md`.

## Two systems in one repo

| Directory | Purpose | Stack |
|---|---|---|
| `.opencode/` | OpenCode ECC plugin config | TypeScript, npm, `tsc` |
| `.agents/skills/` | ECC skill definitions | Markdown |
| *(root)* | **Planned:** ComfyUI Mac toolkit | Python 3.12, uv, pytest, bash |

Do not confuse the plugin config with the Python project. They build independently.

## `.opencode/` — plugin build

- **Build:** `cd .opencode && npm run build` (runs `tsc`). Output is `dist/`.
- **Critical:** Without `.opencode/dist/index.js`, OpenCode detects slash commands but **silently skips plugin hooks and tools**. The installer fails fast if the build step is missing.
- **Skills path:** `.opencode/opencode.json` references skills at `"../skills"`, which resolves to `.agents/skills/`.

## Planned Python project (from `todo.md`)

- **Package manager:** uv
- **Python:** 3.12
- **Entry point:** `render.py` (CLI)
- **Library code:** `lib/` (`preflight.py`, `memcheck.py`, `api.py`)
- **Tests:** `tests/` with pytest + `conftest.py`
- **Scripts:** `install.sh`, `pull_models.sh`, `stage1_verify.py`

## CLI exit codes (`render.py`)

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Not verified / config drifted |
| 2 | ComfyUI not running |
| 3 | Failed after starting |
| 4 | Timeout |

## Important paths

| Path | Meaning |
|---|---|
| `~/projects/comfyui-mac` | This repo (code) |
| `~/comfyui-mac` | **Runtime ComfyUI install** (NOT in repo) |
| `~/.comfyui-mac/verified` | Stage-1 verification flag file |
| `scripts/update_todo.py` | Post-commit hook — run `python scripts/update_todo.py <N>` after each task |

## ComfyUI context

- **Hardware target:** Apple Silicon (MPS backend, not CUDA)
- **Custom nodes:** 6 packs (VideoHelperSuite, ComfyUI-GGUF, HunyuanVideoWrapper, LatentSyncWrapper, Frame-Interpolation, VEnhancer)
- **Dropped nodes:** LTX-Video and WanVideoWrapper have no native MPS path
- **Model downloads:** ~25GB from HuggingFace (LatentSync, HunyuanVideo-GGUF, VEnhancer, RIFE)
- **Workflow JSONs:** Stored in `workflows/` as API-exported `.json` files (not UI graphs)
