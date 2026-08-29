from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from scraper.exceptions import PostbackTargetNotFoundError, TokenExtractionError

HIDDEN_TOKEN_FIELDS = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def _attr_str(tag: Tag, name: str, default: str = "") -> str:
    value = tag.get(name)
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return " ".join(value)


def extract_form_fields(html: str) -> dict[str, str]:

    soup = parse_html(html)
    form = soup.find("form")
    if form is None or not isinstance(form, Tag):
        raise TokenExtractionError("No <form> element found in response body.")

    fields: dict[str, str] = {}

    for tag in form.find_all("input"):
        name = _attr_str(tag, "name")
        if not name:
            continue
        input_type = _attr_str(tag, "type", "text").lower()

        if input_type in ("checkbox", "radio"):
            if tag.has_attr("checked"):
                fields[name] = _attr_str(tag, "value", "on")
            continue

        if input_type == "submit":
            continue

        fields[name] = _attr_str(tag, "value")

    for tag in form.find_all("select"):
        name = _attr_str(tag, "name")
        if not name:
            continue
        selected = tag.find("option", selected=True)
        if selected is None:
            selected = tag.find("option")
        if selected is not None and isinstance(selected, Tag):
            fields[name] = _attr_str(selected, "value", selected.get_text(strip=True))

    for hidden_name in HIDDEN_TOKEN_FIELDS:
        if hidden_name not in fields:
            raise TokenExtractionError(
                f"Expected hidden field '{hidden_name}' was not present in the form."
            )

    return fields


def find_postback_target(html: str, hint: str) -> str:

    soup = parse_html(html)
    for tag in soup.find_all(["a", "input"]):
        onclick = _attr_str(tag, "onclick") or _attr_str(tag, "href")
        if "__doPostBack" in onclick and hint in onclick:
            start = onclick.find("__doPostBack('") + len("__doPostBack('")
            end = onclick.find("'", start)
            if start > -1 and end > -1:
                return onclick[start:end]

    raise PostbackTargetNotFoundError(hint)


def find_row_postback_targets(html: str, hint: str) -> list[str]:

    soup = parse_html(html)
    targets: list[str] = []

    for tag in soup.find_all(["a", "input"]):
        onclick = _attr_str(tag, "onclick") or _attr_str(tag, "href")
        if "__doPostBack" in onclick and hint in onclick:
            start = onclick.find("__doPostBack('") + len("__doPostBack('")
            end = onclick.find("'", start)
            if start > -1 and end > -1:
                targets.append(onclick[start:end])

    return targets
