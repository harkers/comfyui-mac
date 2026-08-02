# ComfyUI on the Mac — Implementation Todo

> Derived from `~/projects/macbookm5promax/docs/superpowers/plans/2026-08-02-comfyui-mac-implementation.md`

---

## Task 1: Repo scaffold
- [x] Create directory structure (`lib/`, `tests/`, `workflows/`, `docs/`)
- [x] Write `pyproject.toml` (uv project, Python 3.12)
- [x] Write `.gitignore`
- [x] Write `custom_nodes.txt` (6-node roster)
- [x] Write `models.sha256` skeleton
- [x] Write `README.md` skeleton
- [x] Create `lib/__init__.py` and workflow placeholder `.gitkeep` files
- [x] Verify structure and commit

**Files created:** 10  
**Tests:** N/A (scaffold only)

---

## Task 2: `lib/preflight.py` + tests
- [x] Write failing tests (`tests/test_preflight.py`) — 3 tests
- [x] Run tests to verify they fail
- [x] Write implementation (`lib/preflight.py`)
- [x] Run tests to verify they pass (3 passed)
- [x] Commit

**Interface:** `PreflightStatus`, `check_verified_flag()`, `check_mps_available()`, `run_preflight()`

---

## Task 3: `lib/memcheck.py` + tests
- [x] Write failing tests (`tests/test_memcheck.py`) — 3 tests
- [x] Run tests to verify they fail
- [x] Write implementation (`lib/memcheck.py`)
- [x] Run tests to verify they pass (3 passed)
- [x] Commit

**Interface:** `available_memory_gb()`, `memory_warning()`

---

## Task 4: `lib/api.py` + tests
- [x] Write `tests/conftest.py` (shared fixtures)
- [x] Write failing tests (`tests/test_api.py`) — 9 tests
- [x] Run tests to verify they fail
- [x] Write implementation (`lib/api.py`) — ComfyClient + submit_with_retry
- [x] Run tests to verify they pass (9 passed)
- [x] Commit

**Interface:** `ComfyClient` (`submit_job`, `poll_status`, `fetch_output`, `interrupt`), `submit_with_retry()`

---

## Task 5: `render.py` + tests
- [ ] Write failing tests (`tests/test_cli.py`) — 7 tests
- [ ] Run tests to verify they fail
- [ ] Write implementation (`render.py`) — CLI with four-mode error contract
- [ ] Run tests to verify they pass (7 passed)
- [ ] Run full test suite (19 total so far)
- [ ] Commit

**Exit codes:** 0=success, 1=not-verified/drifted, 2=not-running, 3=failed-after-starting, 4=timeout

---

## Task 6: `install.sh`
- [ ] Write `install.sh` — preflight, Stage 0, idempotent node/venv setup
- [ ] Make executable and verify syntax (`bash -n`)
- [ ] Commit

**Note:** Do NOT run for real yet — depends on Tasks 7 & 8

---

## Task 7: `pull_models.sh`
- [ ] Write `pull_models.sh` — resumable HF pulls, checksum provenance
- [ ] Make executable and verify syntax (`bash -n`)
- [ ] Commit

**Note:** Do NOT run for real yet — depends on Task 6's Stage 0 dirs

---

## Task 8: `stage1_verify.py` + tests
- [ ] Write failing tests (`tests/test_stage1_verify.py`) — 4 tests
- [ ] Run tests to verify they fail
- [ ] Write implementation (`stage1_verify.py`)
- [ ] Run tests to verify they pass (4 passed)
- [ ] Commit

**Interface:** `run_stage1()`, `Stage1Result`, `write_verified_flag_if_passed()`

---

## Task 9: Author Stage 1 MVR workflows + LatentSync fixture
- [ ] Start ComfyUI manually and open UI (`http://127.0.0.1:8188`)
- [ ] Build + export API workflow JSON for each of 6 node packs:
  - [ ] `01_videohelpersuite_pass.json`
  - [ ] `02_gguf_pass.json`
  - [ ] `03_hunyuanvideowrapper_pass.json`
  - [ ] `04_latentsyncwrapper_pass.json`
  - [ ] `05_frameinterpolation_pass.json`
  - [ ] `06_venhancer_pass.json`
- [ ] Validate each JSON with `jq`
- [ ] Record LatentSync fixture (`latentsync_test.mp4`, under 5MB)
- [ ] Commit

**Note:** Requires live ComfyUI UI — cannot be done blind

---

## Task 10: `README.md`
- [ ] Write full README (roster, MPS caveats, setup/render instructions, security)
- [ ] Verify and commit

---

## Task 11: End-to-end verification on real hardware
- [ ] Run full test suite (23 total)
- [ ] Run `./install.sh` for real (expect possible repin loop)
- [ ] Confirm `pull_models.sh` completed and `models.sha256` populated (~25GB)
- [ ] Confirm Stage 1 passed and `~/.comfyui-mac/verified` exists
- [ ] Real render smoke test (`render.py run` on an MVR workflow)
- [ ] Verify four failure modes for real
- [ ] Re-run Stage 1, commit final state
- [ ] Push to GitHub (`harkers/comfyui-mac`)

---

## Summary

| Metric | Value |
|---|---|
| **Total tasks** | 11 |
| **Unit tests** | 23 (Tasks 2, 3, 4, 5, 8) |
| **Bash scripts** | 2 (`install.sh`, `pull_models.sh`) |
| **Model downloads** | ~25GB (4 models: LatentSync, HunyuanVideo-GGUF, VEnhancer, RIFE) |
| **Custom nodes** | 6 (VideoHelperSuite, ComfyUI-GGUF, HunyuanVideoWrapper, LatentSyncWrapper, Frame-Interpolation, VEnhancer) |
| **Dropped nodes** | 2 (LTX-Video, WanVideoWrapper — no native MPS path) |

**Repo root:** `~/projects/comfyui-mac`  
**ComfyUI home:** `~/comfyui-mac`  
**Verified flag:** `~/.comfyui-mac/verified`
