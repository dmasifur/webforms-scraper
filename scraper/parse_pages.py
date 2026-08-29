

from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from scraper.normalize import clean_text


@dataclass
class StudentRow:
    student_id: str
    name: str
    campus: str
    course: str
    enrolled: str
    status: str


@dataclass
class StudentDetail:
    email: str
    phone: str
    date_of_birth: str
    address: str
    emergency_contact: str


def parse_student_grid(html: str) -> list[StudentRow]:

    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id=lambda v: bool(v) and "gvStudents" in v)
    if table is None or not isinstance(table, Tag):
        return []

    rows: list[StudentRow] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        # Data rows have exactly 7 <td>s: 6 bound columns + the View link column.
        if len(cells) != 7:
            continue
        rows.append(
            StudentRow(
                student_id=clean_text(cells[0].get_text()),
                name=clean_text(cells[1].get_text()),
                campus=clean_text(cells[2].get_text()),
                course=clean_text(cells[3].get_text()),
                enrolled=clean_text(cells[4].get_text()),
                status=clean_text(cells[5].get_text()),
            )
        )
    return rows


def has_next_page(html: str) -> bool:
    
    soup = BeautifulSoup(html, "lxml")
    pager = soup.find("tr", class_="pager")
    if pager is None or not isinstance(pager, Tag):
        return False
   
    found_current = False
    for child in pager.find_all(["span", "a"]):
        if child.name == "span":
            found_current = True
            continue
        if child.name == "a" and found_current:
            return True
    return False


def parse_student_detail(html: str) -> StudentDetail:
    soup = BeautifulSoup(html, "lxml")

    def field(td_id: str) -> str:
        tag = soup.find(id=td_id)
        return clean_text(tag.get_text()) if tag else ""

    return StudentDetail(
        email=field("tdEmail"),
        phone=field("tdPhone"),
        date_of_birth=field("tdDob"),
        address=field("tdAddress"),
        emergency_contact=field("tdEmergency"),
    )