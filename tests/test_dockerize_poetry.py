"""Tests for `dockerize_poetry` module."""


import pytest

import dockerize_poetry


@pytest.fixture()
def version() -> str:
    """Sample pytest fixture."""
    return dockerize_poetry.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.1.0"
