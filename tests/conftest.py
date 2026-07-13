"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def api_key():
    """Sample API key for testing."""
    return "test-key-us5"


@pytest.fixture
def list_id():
    """Sample list ID for testing."""
    return "test-list-id"
