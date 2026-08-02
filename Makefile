.PHONY: test test-preflight test-memcheck test-api test-cli test-stage1 lint todo check install

# Run the full test suite
test:
	uv run pytest tests/ -v

# Run individual test files
test-preflight:
	uv run pytest tests/test_preflight.py -v

test-memcheck:
	uv run pytest tests/test_memcheck.py -v

test-api:
	uv run pytest tests/test_api.py -v

test-cli:
	uv run pytest tests/test_cli.py -v

test-stage1:
	uv run pytest tests/test_stage1_verify.py -v

# Lint and format
lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

# Update todo.md after completing a task (e.g. make todo TASK=2)
todo:
	$(if $(TASK),python3 scripts/update_todo.py $(TASK),@echo "Usage: make todo TASK=<task_number>")

# Verify bash script syntax
check:
	bash -n install.sh || true
	bash -n pull_models.sh || true

# Install dependencies
install:
	uv sync --all-extras
