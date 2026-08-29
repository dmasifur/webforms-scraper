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


def _postback_target_from_onclick(onclick: str) -> str | None:
    if "__doPostBack" not in onclick:
        return None
    start = onclick.find("__doPostBack('") + len("__doPostBack('")
    end = onclick.find("'", start)
    if start > -1 and end > -1:
        return onclick[start:end]
    return None


def find_postback_target(html: str, hint: str) -> str:

    soup = parse_html(html)
    for tag in soup.find_all(["a", "input"]):
        onclick = _attr_str(tag, "onclick") or _attr_str(tag, "href")
        if hint in onclick:
            target = _postback_target_from_onclick(onclick)
            if target is not None:
                return target

    raise PostbackTargetNotFoundError(hint)


def find_row_postback_target(row: Tag, hint: str) -> str | None:
    for tag in row.find_all(["a", "input"]):
        onclick = _attr_str(tag, "onclick") or _attr_str(tag, "href")
        if hint in onclick:
            target = _postback_target_from_onclick(onclick)
            if target is not None:
                return target
    return None


def find_submit_field(html: str, hint: str) -> tuple[str, str]:
    soup = parse_html(html)
    for tag in soup.find_all("input"):
        if _attr_str(tag, "type", "text").lower() != "submit":
            continue
        name = _attr_str(tag, "name")
        if name and hint in name:
            return name, _attr_str(tag, "value")

    raise PostbackTargetNotFoundError(hint)


def _parse_dopostback(raw: str) -> tuple[str, str] | None:
    if "__doPostBack" not in raw:
        return None
    cleaned = raw.replace("\\'", "'").replace('\\"', '"')
    start = cleaned.find("__doPostBack(")
    if start == -1:
        return None
    inner = cleaned[start + len("__doPostBack(") :]
    end = inner.find(")")
    if end == -1:
        return None
    parts = [p.strip().strip("'\"") for p in inner[:end].split(",")]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def find_pager_link(html: str, page_number: int) -> tuple[str, str]:
    soup = parse_html(html)
    pager = soup.find("tr", class_="pager")
    if pager is None or not isinstance(pager, Tag):
        raise PostbackTargetNotFoundError("pager row (tr.pager)")

    for tag in pager.find_all("a"):
        if tag.get_text(strip=True) != str(page_number):
            continue
        parsed = _parse_dopostback(_attr_str(tag, "onclick") or _attr_str(tag, "href"))
        if parsed:
            return parsed

    raise PostbackTargetNotFoundError(f"pager link for page {page_number}")


def find_select_postback_target(html: str, hint: str) -> tuple[str, str]:
    soup = parse_html(html)
    for tag in soup.find_all("select"):
        name = _attr_str(tag, "name")
        if not name or hint not in name:
            continue
        parsed = _parse_dopostback(_attr_str(tag, "onchange"))
        return (name, parsed[0]) if parsed else (name, name)

    raise PostbackTargetNotFoundError(hint)
