"""Shared pytest fixtures for sms_backup_parser tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def minimal_sms_xml():
    return FIXTURES_DIR / "minimal_sms.xml"


@pytest.fixture
def minimal_mms_xml():
    return FIXTURES_DIR / "minimal_mms.xml"


@pytest.fixture
def minimal_calls_xml():
    return FIXTURES_DIR / "minimal_calls.xml"


@pytest.fixture
def mixed_xml():
    return FIXTURES_DIR / "mixed.xml"


@pytest.fixture
def edge_cases_xml():
    return FIXTURES_DIR / "edge_cases.xml"


@pytest.fixture
def malformed_xml():
    return FIXTURES_DIR / "malformed.xml"
