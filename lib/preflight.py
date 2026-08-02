"""Preflight checks for ComfyUI Mac toolkit.

Checks whether the runtime environment is ready to render workflows.
"""

from dataclasses import dataclass
from pathlib import Path

import torch


@dataclass
class PreflightStatus:
    """Result of preflight checks."""

    verified: bool
    mps: bool

    @property
    def ok(self) -> bool:
        """Return True only if all checks pass."""
        return self.verified and self.mps


def check_verified_flag() -> bool:
    """Check whether the Stage-1 verification flag exists.

    Looks for ``~/.comfyui-mac/verified``.
    """
    flag = Path.home() / ".comfyui-mac" / "verified"
    return flag.exists()


def check_mps_available() -> bool:
    """Check whether Apple Silicon MPS backend is available."""
    return torch.backends.mps.is_available()


def run_preflight() -> PreflightStatus:
    """Run all preflight checks and return a status object."""
    return PreflightStatus(
        verified=check_verified_flag(),
        mps=check_mps_available(),
    )
