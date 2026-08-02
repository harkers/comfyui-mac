"""Tests for render.py CLI."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from render import (
    EXIT_FAILED,
    EXIT_NOT_RUNNING,
    EXIT_NOT_VERIFIED,
    EXIT_SUCCESS,
    EXIT_TIMEOUT,
    main,
)


class TestMain:
    def test_returns_0_on_success(self, tmp_path):
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps({"prompt": {}}))

        with patch("render.run_preflight", return_value=Mock(ok=True, verified=True, mps=True)):
            with patch("render.ComfyClient") as MockClient:
                client = MockClient.return_value
                client.submit_job.return_value = "abc-123"
                client.poll_status.return_value = {"outputs": {}}
                client.fetch_output.return_value = [{"filename": "out.png"}]

                assert main(["run", str(wf)]) == EXIT_SUCCESS

    def test_returns_1_when_not_verified(self, tmp_path):
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps({"prompt": {}}))

        with patch("render.run_preflight", return_value=Mock(ok=False, verified=False, mps=True)):
            assert main(["run", str(wf)]) == EXIT_NOT_VERIFIED

    def test_returns_1_when_mps_unavailable(self, tmp_path):
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps({"prompt": {}}))

        with patch("render.run_preflight", return_value=Mock(ok=False, verified=True, mps=False)):
            assert main(["run", str(wf)]) == EXIT_NOT_VERIFIED

    def test_returns_2_when_comfyui_not_running(self, tmp_path):
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps({"prompt": {}}))

        with patch("render.run_preflight", return_value=Mock(ok=True, verified=True, mps=True)):
            with patch("render.ComfyClient") as MockClient:
                client = MockClient.return_value
                client.submit_job.side_effect = ConnectionError("refused")

                assert main(["run", str(wf)]) == EXIT_NOT_RUNNING

    def test_returns_3_on_job_failure(self, tmp_path):
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps({"prompt": {}}))

        with patch("render.run_preflight", return_value=Mock(ok=True, verified=True, mps=True)):
            with patch("render.ComfyClient") as MockClient:
                client = MockClient.return_value
                client.submit_job.return_value = "abc-123"
                client.poll_status.return_value = {"error": "boom"}

                assert main(["run", str(wf)]) == EXIT_FAILED

    def test_returns_4_on_timeout(self, tmp_path):
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps({"prompt": {}}))

        with patch("render.run_preflight", return_value=Mock(ok=True, verified=True, mps=True)):
            with patch("render.ComfyClient") as MockClient:
                client = MockClient.return_value
                client.submit_job.return_value = "abc-123"
                client.poll_status.return_value = {}  # never completes

                with patch("render.time.sleep"):
                    with patch("render.time.time", side_effect=[0, 0, 9999]):  # immediate timeout
                        assert main(["run", str(wf)]) == EXIT_TIMEOUT

    def test_loads_workflow_from_file(self, tmp_path):
        workflow = {"prompt": {"1": {"class_type": "KSampler"}}}
        wf = tmp_path / "wf.json"
        wf.write_text(json.dumps(workflow))

        with patch("render.run_preflight", return_value=Mock(ok=True, verified=True, mps=True)):
            with patch("render.ComfyClient") as MockClient:
                client = MockClient.return_value
                client.submit_job.return_value = "abc-123"
                client.poll_status.return_value = {"outputs": {}}
                client.fetch_output.return_value = []

                main(["run", str(wf)])

                call_args = client.submit_job.call_args[0][0]
                assert call_args == workflow
