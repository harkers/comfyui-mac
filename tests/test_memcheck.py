"""Tests for lib/memcheck.py."""

from unittest.mock import patch

import pytest

from lib.memcheck import available_memory_gb, memory_warning


class TestAvailableMemoryGb:
    def test_returns_memory_value(self):
        # 16 GiB in bytes = 16 * 1024**3
        with patch("psutil.virtual_memory", return_value=MockMem(total=34_359_738_368, available=17_179_869_184)):
            assert available_memory_gb() == 16.0

    def test_returns_zero_when_no_memory_available(self):
        with patch("psutil.virtual_memory", return_value=MockMem(total=32_000_000_000, available=0)):
            assert available_memory_gb() == 0.0


class TestMemoryWarning:
    def test_returns_warning_when_below_threshold(self):
        with patch("lib.memcheck.available_memory_gb", return_value=2.0):
            assert "low" in memory_warning(threshold_gb=4.0).lower()

    def test_returns_none_when_above_threshold(self):
        with patch("lib.memcheck.available_memory_gb", return_value=16.0):
            assert memory_warning(threshold_gb=4.0) is None


class MockMem:
    def __init__(self, total: int, available: int):
        self.total = total
        self.available = available
