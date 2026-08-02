"""ComfyUI API client for the Mac toolkit.

Thin wrapper around ComfyUI's HTTP API with retry support.
"""

import time
from typing import Any

import requests


class ComfyClient:
    """HTTP client for ComfyUI's API."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def submit_job(self, workflow: dict[str, Any]) -> str:
        """Submit a workflow and return the prompt_id."""
        resp = requests.post(
            f"{self.base_url}/prompt",
            json=workflow,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["prompt_id"]

    def poll_status(self, prompt_id: str) -> dict[str, Any]:
        """Poll execution status for *prompt_id*.

        Returns the entry from ``/history/{prompt_id}`` or an empty dict
        if not yet present.
        """
        resp = requests.get(
            f"{self.base_url}/history/{prompt_id}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get(prompt_id, {})

    def fetch_output(self, prompt_id: str) -> list[dict[str, Any]]:
        """Fetch output file metadata for a completed job."""
        resp = requests.get(
            f"{self.base_url}/history/{prompt_id}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        entry = data.get(prompt_id, {})
        outputs = entry.get("outputs", {})
        files: list[dict[str, Any]] = []
        for node_id, node_outputs in outputs.items():
            images = node_outputs.get("images", [])
            files.extend(images)
        return files

    def interrupt(self) -> None:
        """Send an interrupt signal to ComfyUI."""
        resp = requests.post(f"{self.base_url}/interrupt", timeout=10)
        resp.raise_for_status()


def submit_with_retry(
    client: ComfyClient,
    workflow: dict[str, Any],
    *,
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> str:
    """Submit a workflow with exponential backoff on transient errors.

    Raises the last exception if all retries are exhausted.
    """
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            return client.submit_job(workflow)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt < max_retries - 1:
                time.sleep(backoff_seconds * (2**attempt))
    raise last_err
