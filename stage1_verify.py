#!/usr/bin/env python3
"""Stage 1 verification for ComfyUI Mac toolkit.

Checks that the ComfyUI runtime environment is correctly set up.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import torch


@dataclass
class Stage1Result:
    """Result of Stage 1 verification checks."""

    passed: bool
    comfyui_home: bool
    custom_nodes: bool
    mps: bool


def _parse_custom_nodes(path: Path) -> list[str]:
    """Read custom_nodes.txt and return list of repo names (e.g. 'ComfyUI-VideoHelperSuite')."""
    repos: list[str] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            repo_name = stripped.split("/")[-1]
            repos.append(repo_name)
    return repos


def _check_custom_nodes(comfyui_home: Path, repos: list[str]) -> bool:
    nodes_dir = comfyui_home / "custom_nodes"
    for repo in repos:
        if not (nodes_dir / repo).is_dir():
            return False
    return True


def run_stage1(*, custom_nodes_file: Path | None = None) -> Stage1Result:
    """Run Stage 1 checks and return a result object."""
    comfyui_home = Path.home() / "comfyui-mac"
    comfyui_ok = comfyui_home.is_dir()

    nodes_ok = True
    if custom_nodes_file and custom_nodes_file.exists():
        repos = _parse_custom_nodes(custom_nodes_file)
        nodes_ok = _check_custom_nodes(comfyui_home, repos)
    elif custom_nodes_file:
        nodes_ok = False

    mps_ok = torch.backends.mps.is_available()

    return Stage1Result(
        passed=comfyui_ok and nodes_ok and mps_ok,
        comfyui_home=comfyui_ok,
        custom_nodes=nodes_ok,
        mps=mps_ok,
    )


def write_verified_flag_if_passed(result: Stage1Result) -> None:
    """Write the verified flag if Stage 1 passed."""
    if not result.passed:
        return
    flag_dir = Path.home() / ".comfyui-mac"
    flag_dir.mkdir(parents=True, exist_ok=True)
    flag = flag_dir / "verified"
    flag.write_text("stage1-verified\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = __import__("argparse").ArgumentParser(description="Stage 1 verification")
    parser.add_argument("--custom-nodes", type=Path, default=Path("custom_nodes.txt"))
    args = parser.parse_args(argv)

    result = run_stage1(custom_nodes_file=args.custom_nodes)

    print(f"comfyui_home : {result.comfyui_home}")
    print(f"custom_nodes : {result.custom_nodes}")
    print(f"mps          : {result.mps}")
    print(f"passed       : {result.passed}")

    write_verified_flag_if_passed(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
