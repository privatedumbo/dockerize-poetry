"""Tests for `dockerize_poetry` module."""

from typing import Generator

import dockerize_poetry
import pytest


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield dockerize_poetry.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.1.0"
