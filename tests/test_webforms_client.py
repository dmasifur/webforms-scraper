import pytest
import requests_mock as rm

from scraper.exceptions import LoginFailedError, UnexpectedResponseError
from scraper.webforms_client import WebFormsClient

BASE = "http://localhost:51286"


@pytest.fixture
def client() -> WebFormsClient:
    return WebFormsClient(BASE, delay_seconds=0)


def test_login_sends_the_submit_button(
    client: WebFormsClient, login_page: str, list_page_2: str, requests_mock: rm.Mocker
) -> None:
    requests_mock.get(f"{BASE}/Login.aspx", text=login_page)
    requests_mock.post(f"{BASE}/Login.aspx", text=list_page_2)

    client.login("demo", "demo123", login_path="/Login.aspx")

    request = requests_mock.last_request
    assert request is not None
    body = request.text or ""

    assert "ctl00%24Main%24btnLogin=Sign+in" in body
    assert "ctl00%24Main%24txtUser=demo" in body


def test_login_raises_when_login_page_is_returned(
    client: WebFormsClient, login_page: str, requests_mock: rm.Mocker
) -> None:
    requests_mock.get(f"{BASE}/Login.aspx", text=login_page)
    requests_mock.post(f"{BASE}/Login.aspx", text=login_page)

    with pytest.raises(LoginFailedError):
        client.login("demo", "wrong", login_path="/Login.aspx")


def test_postback_uses_exact_target_without_re_resolving(
    client: WebFormsClient, list_page_2: str, requests_mock: rm.Mocker
) -> None:

    requests_mock.post(f"{BASE}/Default.aspx", text=list_page_2)

    client.postback(list_page_2, "/Default.aspx", target="ctl00$Main$gvStudents", argument="Page$3")
    request = requests_mock.last_request
    assert request is not None
    body = request.text or ""
    assert "__EVENTTARGET=ctl00%24Main%24gvStudents&" in body
    assert "lnkDetail" not in body
    assert "__EVENTARGUMENT=Page%243" in body


def test_postback_applies_extra_fields(
    client: WebFormsClient, list_page_2: str, requests_mock: rm.Mocker
) -> None:
    requests_mock.post(f"{BASE}/Default.aspx", text=list_page_2)

    client.postback(
        list_page_2,
        "/Default.aspx",
        target="ctl00$Main$ddlCampus",
        extra_fields={"ctl00$Main$ddlCampus": "Westfield"},
    )
    request = requests_mock.last_request
    assert request is not None
    assert "ctl00%24Main%24ddlCampus=Westfield" in (request.text or "")


def test_postback_requires_a_target(client: WebFormsClient, list_page_2: str) -> None:
    with pytest.raises(ValueError):
        client.postback(list_page_2, "/Default.aspx")


def test_client_error_is_not_retried(client: WebFormsClient, requests_mock: rm.Mocker) -> None:
    requests_mock.get(f"{BASE}/Default.aspx", status_code=404, text="not found")

    with pytest.raises(UnexpectedResponseError):
        client.get("/Default.aspx")

    assert requests_mock.call_count == 1


def test_server_error_is_retried_then_raises(
    client: WebFormsClient, requests_mock: rm.Mocker
) -> None:
    requests_mock.get(f"{BASE}/Default.aspx", status_code=500, text="server error")

    with pytest.raises(UnexpectedResponseError) as excinfo:
        client.get("/Default.aspx")

    assert requests_mock.call_count == 3  # DEFAULT_MAX_RETRIES
    assert "server error" in str(excinfo.value)  # body is surfaced for diagnosis


def test_server_error_recovers_on_retry(
    client: WebFormsClient, list_page_2: str, requests_mock: rm.Mocker
) -> None:
    requests_mock.get(
        f"{BASE}/Default.aspx",
        [{"status_code": 500, "text": "boom"}, {"status_code": 200, "text": list_page_2}],
    )

    assert "gvStudents" in client.get("/Default.aspx")
    assert requests_mock.call_count == 2
