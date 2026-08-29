from __future__ import annotations

import pytest

from scraper.exceptions import PostbackTargetNotFoundError, TokenExtractionError
from scraper.forms import (
    HIDDEN_TOKEN_FIELDS,
    extract_form_fields,
    find_pager_link,
    find_select_postback_target,
    find_submit_field,
)


def test_extract_form_fields_captures_all_hidden_tokens(list_page_2: str) -> None:
    fields = extract_form_fields(list_page_2)
    for token in HIDDEN_TOKEN_FIELDS:
        assert token in fields
        assert fields[token], f"{token} should not be empty"


def test_extract_form_fields_omits_submit_buttons(login_page: str) -> None:
    fields = extract_form_fields(login_page)
    assert "ctl00$Main$btnLogin" not in fields
    assert "ctl00$Main$txtUser" in fields


def test_extract_form_fields_echoes_selected_option(list_page_filtered: str) -> None:
    fields = extract_form_fields(list_page_filtered)
    assert fields["ctl00$Main$ddlCampus"] == "Westfield"


def test_extract_form_fields_defaults_to_first_option(list_page_2: str) -> None:
    fields = extract_form_fields(list_page_2)
    assert fields["ctl00$Main$ddlCampus"] == ""


def test_extract_form_fields_rejects_page_without_form() -> None:
    with pytest.raises(TokenExtractionError):
        extract_form_fields("<html><body><p>no form here</p></body></html>")


def test_find_submit_field_returns_name_and_value(login_page: str) -> None:
    name, value = find_submit_field(login_page, "btnLogin")
    assert name == "ctl00$Main$btnLogin"
    assert value == "Sign in"


def test_find_pager_link_returns_matching_target_and_argument(list_page_2: str) -> None:
    target, argument = find_pager_link(list_page_2, 3)
    assert target == "ctl00$Main$gvStudents"
    assert argument == "Page$3"


def test_find_pager_link_never_returns_a_row_link(list_page_2: str) -> None:
    target, _ = find_pager_link(list_page_2, 4)
    assert "lnkDetail" not in target


def test_find_pager_link_raises_for_current_page(list_page_2: str) -> None:
    with pytest.raises(PostbackTargetNotFoundError):
        find_pager_link(list_page_2, 2)


def test_find_select_postback_target_unescapes_autopostback(list_page_2: str) -> None:
    field_name, event_target = find_select_postback_target(list_page_2, "ddlCampus")
    assert field_name == "ctl00$Main$ddlCampus"
    assert event_target == "ctl00$Main$ddlCampus"
    assert "\\" not in event_target


def test_find_select_postback_target_raises_when_absent(detail_page: str) -> None:
    with pytest.raises(PostbackTargetNotFoundError):
        find_select_postback_target(detail_page, "ddlCampus")
