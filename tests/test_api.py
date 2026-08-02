"""Tests for lib/api.py."""

import json
from unittest.mock import Mock, patch

import pytest

from lib.api import ComfyClient, submit_with_retry


class TestComfyClientSubmitJob:
    def test_posts_to_api(self, base_url, sample_workflow):
        client = ComfyClient(base_url)
        mock_resp = Mock()
        mock_resp.json.return_value = {"prompt_id": "abc-123"}
        mock_resp.raise_for_status.return_value = None

        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = client.submit_job(sample_workflow)

        mock_post.assert_called_once_with(
            f"{base_url}/prompt",
            json=sample_workflow,
            timeout=30,
        )
        assert result == "abc-123"

    def test_raises_on_connection_error(self, base_url, sample_workflow):
        client = ComfyClient(base_url)
        with patch("requests.post", side_effect=ConnectionError("refused")):
            with pytest.raises(ConnectionError):
                client.submit_job(sample_workflow)


class TestComfyClientPollStatus:
    def test_returns_status(self, base_url):
        client = ComfyClient(base_url)
        mock_resp = Mock()
        mock_resp.json.return_value = {"abc-123": {"outputs": {}}}
        mock_resp.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_resp) as mock_get:
            status = client.poll_status("abc-123")

        mock_get.assert_called_once_with(
            f"{base_url}/history/abc-123",
            timeout=10,
        )
        assert status == {"outputs": {}}

    def test_returns_empty_when_not_found(self, base_url):
        client = ComfyClient(base_url)
        mock_resp = Mock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_resp):
            status = client.poll_status("abc-123")

        assert status == {}


class TestComfyClientFetchOutput:
    def test_returns_output_files(self, base_url):
        client = ComfyClient(base_url)
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "abc-123": {
                "outputs": {
                    "1": {"images": [{"filename": "out.png", "type": "output"}]},
                },
            },
        }
        mock_resp.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_resp):
            files = client.fetch_output("abc-123")

        assert files == [{"filename": "out.png", "type": "output"}]

    def test_returns_empty_list_when_no_outputs(self, base_url):
        client = ComfyClient(base_url)
        mock_resp = Mock()
        mock_resp.json.return_value = {"abc-123": {"outputs": {}}}
        mock_resp.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_resp):
            files = client.fetch_output("abc-123")

        assert files == []


class TestComfyClientInterrupt:
    def test_posts_interrupt(self, base_url):
        client = ComfyClient(base_url)
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None

        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.interrupt()

        mock_post.assert_called_once_with(f"{base_url}/interrupt", timeout=10)


class TestSubmitWithRetry:
    def test_succeeds_first_try(self, base_url, sample_workflow):
        client = ComfyClient(base_url)
        with patch.object(client, "submit_job", return_value="abc-123"):
            result = submit_with_retry(client, sample_workflow)
        assert result == "abc-123"

    def test_retries_on_transient_error(self, base_url, sample_workflow):
        client = ComfyClient(base_url)
        with patch.object(client, "submit_job", side_effect=[RuntimeError("500"), "abc-123"]):
            result = submit_with_retry(client, sample_workflow, max_retries=2, backoff_seconds=0)
        assert result == "abc-123"

    def test_raises_after_max_retries(self, base_url, sample_workflow):
        client = ComfyClient(base_url)
        with patch.object(client, "submit_job", side_effect=RuntimeError("500")):
            with pytest.raises(RuntimeError, match="500"):
                submit_with_retry(client, sample_workflow, max_retries=2, backoff_seconds=0)
