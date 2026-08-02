#!/usr/bin/env python3
"""ComfyUI Mac toolkit — CLI entry point.

Usage:
    render.py run <workflow.json> [--url URL] [--timeout SECONDS]
"""

import argparse
import json
import sys
import time
from pathlib import Path

from lib.api import ComfyClient
from lib.preflight import run_preflight

# Exit codes — must stay in sync with AGENTS.md and tests
EXIT_SUCCESS = 0
EXIT_NOT_VERIFIED = 1
EXIT_NOT_RUNNING = 2
EXIT_FAILED = 3
EXIT_TIMEOUT = 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a ComfyUI workflow")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a workflow JSON")
    run_parser.add_argument("workflow", type=Path, help="Path to workflow JSON")
    run_parser.add_argument("--url", default="http://127.0.0.1:8188", help="ComfyUI base URL")
    run_parser.add_argument("--timeout", type=int, default=300, help="Max seconds to wait for job")

    args = parser.parse_args(argv)

    if args.command != "run":
        parser.print_help()
        return EXIT_NOT_VERIFIED

    # 1. Preflight
    status = run_preflight()
    if not status.ok:
        print(f"Preflight failed: verified={status.verified}, mps={status.mps}", file=sys.stderr)
        return EXIT_NOT_VERIFIED

    # 2. Load workflow
    with args.workflow.open("r", encoding="utf-8") as fh:
        workflow = json.load(fh)

    # 3. Submit
    client = ComfyClient(args.url)
    try:
        prompt_id = client.submit_job(workflow)
    except ConnectionError:
        print("ComfyUI is not running", file=sys.stderr)
        return EXIT_NOT_RUNNING
    except Exception as exc:  # noqa: BLE001
        print(f"Submit failed: {exc}", file=sys.stderr)
        return EXIT_FAILED

    # 4. Poll
    start = time.time()
    while True:
        if time.time() - start > args.timeout:
            print("Timed out waiting for job", file=sys.stderr)
            return EXIT_TIMEOUT

        job_status = client.poll_status(prompt_id)
        if job_status.get("error"):
            print(f"Job failed: {job_status['error']}", file=sys.stderr)
            return EXIT_FAILED

        if job_status.get("outputs") is not None:
            break

        time.sleep(1.0)

    # 5. Fetch output
    outputs = client.fetch_output(prompt_id)
    for f in outputs:
        print(f["filename"])

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
