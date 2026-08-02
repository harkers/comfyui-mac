"""Tests for stage1_verify.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from stage1_verify import run_stage1, write_verified_flag_if_passed, Stage1Result


class TestRunStage1:
    def test_passes_when_all_checks_ok(self, tmp_path, monkeypatch):
        # Set up fake ComfyUI home
        comfyui = tmp_path / "comfyui-mac"
        comfyui.mkdir()

        # Fake custom nodes
        nodes_txt = tmp_path / "custom_nodes.txt"
        nodes_txt.write_text("comfyanonymous/ComfyUI-VideoHelperSuite\n")
        nodes_dir = comfyui / "custom_nodes" / "ComfyUI-VideoHelperSuite"
        nodes_dir.mkdir(parents=True)

        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("torch.backends.mps.is_available", return_value=True):
            result = run_stage1(custom_nodes_file=nodes_txt)

        assert result.passed is True
        assert result.comfyui_home is True
        assert result.custom_nodes is True
        assert result.mps is True

    def test_fails_when_comfyui_home_missing(self, tmp_path, monkeypatch):
        nodes_txt = tmp_path / "custom_nodes.txt"
        nodes_txt.write_text("")
        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("torch.backends.mps.is_available", return_value=True):
            result = run_stage1(custom_nodes_file=nodes_txt)

        assert result.passed is False
        assert result.comfyui_home is False

    def test_fails_when_custom_node_missing(self, tmp_path, monkeypatch):
        comfyui = tmp_path / "comfyui-mac"
        comfyui.mkdir()

        nodes_txt = tmp_path / "custom_nodes.txt"
        nodes_txt.write_text("comfyanonymous/ComfyUI-VideoHelperSuite\n")
        # Intentionally NOT creating the node dir

        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("torch.backends.mps.is_available", return_value=True):
            result = run_stage1(custom_nodes_file=nodes_txt)

        assert result.passed is False
        assert result.custom_nodes is False

    def test_fails_when_mps_unavailable(self, tmp_path, monkeypatch):
        comfyui = tmp_path / "comfyui-mac"
        comfyui.mkdir()

        nodes_txt = tmp_path / "custom_nodes.txt"
        nodes_txt.write_text("")

        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("torch.backends.mps.is_available", return_value=False):
            result = run_stage1(custom_nodes_file=nodes_txt)

        assert result.passed is False
        assert result.mps is False


class TestWriteVerifiedFlag:
    def test_writes_flag_when_passed(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        result = Stage1Result(passed=True, comfyui_home=True, custom_nodes=True, mps=True)
        write_verified_flag_if_passed(result)
        assert (tmp_path / ".comfyui-mac" / "verified").exists()

    def test_does_not_write_flag_when_failed(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        result = Stage1Result(passed=False, comfyui_home=True, custom_nodes=False, mps=True)
        write_verified_flag_if_passed(result)
        assert not (tmp_path / ".comfyui-mac" / "verified").exists()
