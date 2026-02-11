"""Pytest configuration and shared fixtures for pedanticran tests."""

import sys
from pathlib import Path

import pytest

# Add the action/ directory to sys.path so we can import check
ACTION_DIR = Path(__file__).parent.parent / "action"
sys.path.insert(0, str(ACTION_DIR))

import check  # noqa: E402

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def clean_pkg():
    """Path to the clean R package fixture."""
    return FIXTURES_DIR / "clean-pkg"


@pytest.fixture
def problematic_pkg():
    """Path to the problematic R package fixture."""
    return FIXTURES_DIR / "problematic-pkg"


@pytest.fixture
def edge_cases_pkg():
    """Path to the edge cases R package fixture."""
    return FIXTURES_DIR / "edge-cases"


@pytest.fixture
def clean_desc(clean_pkg):
    """Parsed DESCRIPTION from the clean package."""
    return check.parse_description(clean_pkg)


@pytest.fixture
def problematic_desc(problematic_pkg):
    """Parsed DESCRIPTION from the problematic package."""
    return check.parse_description(problematic_pkg)


@pytest.fixture
def edge_cases_desc(edge_cases_pkg):
    """Parsed DESCRIPTION from the edge cases package."""
    return check.parse_description(edge_cases_pkg)
