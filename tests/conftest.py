"""Shared fixtures for the test suite."""

import pytest


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8188"


@pytest.fixture
def sample_workflow():
    return {"prompt": {"1": {"class_type": "LoadImage", "inputs": {"image": "test.png"}}}}
