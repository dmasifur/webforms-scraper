from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8", errors="replace")


@pytest.fixture(scope="session")
def login_page() -> str:
    return _load("login_page.html")


@pytest.fixture(scope="session")
def list_page_2() -> str:
    return _load("list_page_2.html")


@pytest.fixture(scope="session")
def list_page_filtered() -> str:
    return _load("list_page_filtered.html")


@pytest.fixture(scope="session")
def detail_page() -> str:
    return _load("detail_page.html")
