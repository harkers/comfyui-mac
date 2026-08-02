"""Tests for lib/preflight.py."""

import os
from unittest.mock import patch

import pytest

from lib.preflight import check_mps_available, check_verified_flag, run_preflight


class TestCheckVerifiedFlag:
    def test_returns_true_when_flag_file_exists(self, tmp_path, monkeypatch):
        flag = tmp_path / ".comfyui-mac" / "verified"
        flag.parent.mkdir()
        flag.touch()
        monkeypatch.setenv("HOME", str(tmp_path))
        assert check_verified_flag() is True

    def test_returns_false_when_flag_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        assert check_verified_flag() is False


class TestCheckMpsAvailable:
    def test_returns_true_when_mps_is_available(self):
        with patch("torch.backends.mps.is_available", return_value=True):
            assert check_mps_available() is True

    def test_returns_false_when_mps_is_unavailable(self):
        with patch("torch.backends.mps.is_available", return_value=False):
            assert check_mps_available() is False


class TestRunPreflight:
    def test_returns_status_with_all_checks(self, tmp_path, monkeypatch):
        flag = tmp_path / ".comfyui-mac" / "verified"
        flag.parent.mkdir()
        flag.touch()
        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("torch.backends.mps.is_available", return_value=True):
            status = run_preflight()

        assert status.verified is True
        assert status.mps is True
        assert status.ok is True

    def test_returns_status_with_failures(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("torch.backends.mps.is_available", return_value=False):
            status = run_preflight()

        assert status.verified is False
        assert status.mps is False
        assert status.ok is False
