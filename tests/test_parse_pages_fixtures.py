from __future__ import annotations

from scraper.parse_pages import has_next_page, parse_student_detail, parse_student_grid


def test_parse_grid_reads_every_row(list_page_2: str) -> None:
    rows = parse_student_grid(list_page_2)
    assert len(rows) == 20  # PageSize=20


def test_parse_grid_ignores_pager_row(list_page_2: str) -> None:
    rows = parse_student_grid(list_page_2)
    assert all(row.student_id.startswith("STU-") for row in rows)


def test_each_row_carries_its_own_detail_target(list_page_2: str) -> None:
    rows = parse_student_grid(list_page_2)
    targets = [row.detail_target for row in rows]
    assert len(set(targets)) == len(targets), "targets must be unique per row"
    assert all("lnkDetail" in t for t in targets)


def test_first_row_matches_fixture(list_page_2: str) -> None:
    row = parse_student_grid(list_page_2)[0]
    assert row.student_id == "STU-10020"
    assert row.name == "Hana Castillo"
    assert row.campus == "Northbridge"
    assert row.detail_target == "ctl00$Main$gvStudents$ctl02$lnkDetail"


def test_filtered_grid_rows_share_the_filtered_campus(list_page_filtered: str) -> None:
    rows = parse_student_grid(list_page_filtered)
    assert rows
    assert {row.campus for row in rows} == {"Westfield"}


def test_has_next_page_true_when_later_pages_linked(list_page_2: str) -> None:
    assert has_next_page(list_page_2) is True


def test_has_next_page_false_without_a_pager(detail_page: str) -> None:
    assert has_next_page(detail_page) is False


def test_detail_page_yields_no_grid_rows(detail_page: str) -> None:
    assert parse_student_grid(detail_page) == []


def test_parse_student_detail_reads_all_fields(detail_page: str) -> None:
    detail = parse_student_detail(detail_page)
    assert detail.email == "sundar.grimaldi9@example.edu"
    assert detail.phone == "0435 340 611"
    assert detail.date_of_birth == "13/05/1985"
    assert detail.address == "25 Jacaranda Street, Westfield"
    assert detail.emergency_contact == "Yusuf Grimaldi (0473 104 149)"


def test_parse_student_detail_is_blank_on_a_list_page(list_page_2: str) -> None:
    detail = parse_student_detail(list_page_2)
    assert detail.email == ""
