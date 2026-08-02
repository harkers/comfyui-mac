# ComfyUI-Mac Loop Runbook

| Property | Value |
|----------|-------|
| Pattern | sequential |
| Mode | safe |
| Branch | main |
| Start commit | 390a615 |

## Remaining Tasks (from todo.md)

| # | Task | Priority | Status |
|---|------|----------|--------|
| 2 | lib/preflight.py + tests | high | pending |
| 3 | lib/memcheck.py + tests | high | pending |
| 4 | lib/api.py + tests/conftest.py | high | pending |
| 5 | render.py + tests | high | pending |
| 6 | install.sh | medium | pending |
| 7 | pull_models.sh | medium | pending |
| 8 | stage1_verify.py + tests | medium | pending |
| 9 | MVR workflows + LatentSync fixture | low | pending |
| 10 | README.md | low | pending |
| 11 | End-to-end verification on real hardware | low | pending |

## Iteration Rules

1. Pick the next uncompleted task in order.
2. TDD: write failing tests first, then implementation.
3. Run only the relevant test file until green, then run the full suite.
4. Commit with a task-specific message.
5. **Post-commit hook:** Run `python scripts/update_todo.py <task_number>` to mark all items in the task as complete in `todo.md`.

## Stop Conditions

- All tasks completed (commit with "Task 11: ..." or equivalent).
- User interrupts with "stop" or "pause".
- Test suite fails unexpectedly (not due to a task under development).
- Out of disk / memory / API quota.

## Command Reference

```bash
# Run single test file
uv run pytest tests/test_preflight.py -v
uv run pytest tests/test_memcheck.py -v
uv run pytest tests/test_api.py -v
uv run pytest tests/test_cli.py -v
uv run pytest tests/test_stage1_verify.py -v

# Run full suite
uv run pytest tests/ -v

# Lint + typecheck
uv run ruff check .
```

## Safety Profile

- `ECC_HOOK_PROFILE=standard` (not overridden)
- `ECC_DISABLED_HOOKS=` (none)
- Pre-commit: run relevant tests before each commit.
- Post-edit: ruff lint pass.
