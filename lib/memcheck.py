"""Memory checks for ComfyUI Mac toolkit."""

import psutil


def available_memory_gb() -> float:
    """Return available system memory in gigabytes (rounded to 1 decimal)."""
    mem = psutil.virtual_memory()
    return round(mem.available / (1024**3), 1)


def memory_warning(threshold_gb: float = 4.0) -> str | None:
    """Return a warning string if available memory is below *threshold_gb*.

    Returns ``None`` when there is sufficient memory.
    """
    available = available_memory_gb()
    if available < threshold_gb:
        return f"WARNING: Low memory ({available:.1f} GB available, {threshold_gb:.1f} GB recommended)"
    return None
