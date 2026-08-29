from __future__ import annotations

from datetime import datetime

from scraper.normalize import clean_text, parse_date


def test_parse_date_reads_the_apps_format() -> None:
    assert parse_date("21/08/2024") == datetime(2024, 8, 21)


def test_parse_date_is_day_first_not_month_first() -> None:
    assert parse_date("13/05/1985") == datetime(1985, 5, 13)


def test_parse_date_returns_none_for_blank_or_invalid() -> None:
    assert parse_date("") is None
    assert parse_date("   ") is None
    assert parse_date("not a date") is None


def test_clean_text_collapses_whitespace() -> None:
    assert clean_text("  Hana   Castillo\n\t") == "Hana Castillo"
