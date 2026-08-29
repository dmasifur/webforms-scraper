from __future__ import annotations

import logging
import time
from types import TracebackType

import requests

from scraper.exceptions import LoginFailedError, UnexpectedResponseError
from scraper.forms import extract_form_fields, find_postback_target, find_submit_field

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15
DEFAULT_DELAY_SECONDS = 1.0
DEFAULT_MAX_RETRIES = 3


class WebFormsClient:
    def __init__(
        self,
        base_url: str,
        *,
        delay_seconds: float = DEFAULT_DELAY_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
        user_agent: str = "webforms-scraping-demo/1.0 (+github.com/dmasifur/webforms-scraping-demo)",  # noqa: E501
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def __enter__(self) -> WebFormsClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.session.close()

    def _full_url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs: object) -> requests.Response:
        url = self._full_url(path)
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)  # type: ignore[arg-type]
                if response.status_code >= 500:
                    raise UnexpectedResponseError(response.status_code, url, response.text[:2000])
                if response.status_code >= 400:
                    # 4xx is not retried — retrying won't fix a bad request or auth failure.
                    raise UnexpectedResponseError(response.status_code, url, response.text[:2000])
                return response
            except (requests.RequestException, UnexpectedResponseError) as exc:
                last_error = exc
                is_last_attempt = attempt == self.max_retries
                is_client_error = isinstance(exc, UnexpectedResponseError) and exc.status_code < 500
                if is_client_error or is_last_attempt:
                    raise
                backoff = self.delay_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "Request to %s failed (attempt %d/%d): %s — retrying in %.1fs",
                    url,
                    attempt,
                    self.max_retries,
                    exc,
                    backoff,
                )
                time.sleep(backoff)

        assert last_error is not None
        raise last_error

    def get(self, path: str) -> str:
        time.sleep(self.delay_seconds)
        response = self._request("GET", path)
        return response.text

    def submit(
        self, current_html: str, path: str, extra_fields: dict[str, str] | None = None
    ) -> str:

        fields = extract_form_fields(current_html)
        if extra_fields:
            fields.update(extra_fields)

        time.sleep(self.delay_seconds)
        response = self._request("POST", path, data=fields)
        return response.text

    def postback(
        self,
        current_html: str,
        path: str,
        *,
        target: str | None,
        target_hint: str | None = None,
        argument: str = "",
        extra_fields: dict[str, str] | None = None,
    ) -> str:

        if target is None:
            if target_hint is None:
                raise ValueError("Provide either target or target_hints")

            target = find_postback_target(current_html, target_hint)

        fields = extract_form_fields(current_html)
        fields["__EVENTTARGET"] = target
        fields["__EVENTARGUMENT"] = argument

        if extra_fields:
            fields.update(extra_fields)

        time.sleep(self.delay_seconds)
        response = self._request("POST", path, data=fields)
        return response.text

    def login(
        self, username: str, password: str, *, login_path: str, submit_hint: str = "btnLogin"
    ) -> str:

        login_html = self.get(login_path)
        fields = extract_form_fields(login_html)

        for name in fields:
            if "txtUser" in name:
                fields[name] = username
            elif "txtPass" in name:
                fields[name] = password

        button_name, button_value = find_submit_field(login_html, submit_hint)
        fields[button_name] = button_value
        time.sleep(self.delay_seconds)
        response = self._request("POST", login_path, data=fields)
        result_html = response.text

        if "txtPass" in result_html or "lblError" in result_html:
            raise LoginFailedError()

        logger.info("Login succeeded for user '%s'", username)
        return result_html
