from __future__ import annotations


class WebFormsError(Exception):
    """Base class for all errors raised by this package."""


class LoginFailedError(WebFormsError):
    """Raised when Forms authentication does not succeed."""

    def __init__(self, message: str = "Login failed: check credentials.") -> None:
        super().__init__(message)


class TokenExtractionError(WebFormsError):
    """Raised when __VIEWSTATE / __EVENTVALIDATION cannot be found in a response.

    Usually means the page didn't render a <form runat="server"> at all, i.e.
    you're looking at a login/error page you didn't expect.
    """


class PostbackTargetNotFoundError(WebFormsError):
    """Raised when a requested postback control cannot be located in the DOM."""

    def __init__(self, target_hint: str) -> None:
        super().__init__(f"No postback control matching '{target_hint}' was found.")
        self.target_hint = target_hint


class UnexpectedResponseError(WebFormsError):
    """Raised when the server responds with a non-2xx status or an unreadable body."""

    def __init__(self, status_code: int, url: str, body_snippet: str = "") -> None:

        message = f"Unexpected response {status_code} from {url}"

        if body_snippet:
            message += f"\n --- response body (first 2000 chars) ---\n {body_snippet}"

        super().__init__(message)
        self.status_code = status_code
        self.url = url
