from __future__ import annotations

from scraper.parse_pages import parse_student_grid

GRID_HTML = """
<html><body><form id="f">
<table id="gvStudents">
  <tr><th>ID</th><th>Name</th><th>Campus</th><th>Course</th><th>Enrolled</th><th>Status</th><th></th></tr>
  <tr>
    <td>STU-10000</td><td>Amara Abbott</td><td>Northbridge</td>
    <td>Diploma of IT</td><td>01/02/2023</td><td>Active</td>
    <td><a href="javascript:__doPostBack('gvStudents$ctl02$lnkDetail','')">View</a></td>
  </tr>
  <tr>
    <td>STU-10001</td><td>Beatriz Bianchi</td><td>Eastgate</td>
    <td>Cert IV</td><td>02/02/2023</td><td>Deferred</td>
    <td><a href="javascript:__doPostBack('gvStudents$ctl03$lnkDetail','')">View</a></td>
  </tr>
</table>
</form></body></html>
"""

GRID_HTML_WITH_SPURIOUS_ROW = """
<html><body><form id="f">
<table id="gvStudents">
  <tr>
    <td>STU-10000</td><td>Amara Abbott</td><td>Northbridge</td>
    <td>Diploma of IT</td><td>01/02/2023</td><td>Active</td>
    <td><a href="javascript:__doPostBack('gvStudents$ctl02$lnkDetail','')">View</a></td>
  </tr>
  <tr>
    <td>Total</td><td>2 records</td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr>
    <td>STU-10001</td><td>Beatriz Bianchi</td><td>Eastgate</td>
    <td>Cert IV</td><td>02/02/2023</td><td>Deferred</td>
    <td><a href="javascript:__doPostBack('gvStudents$ctl04$lnkDetail','')">View</a></td>
  </tr>
</table>
</form></body></html>
"""


def test_parse_student_grid_captures_each_rows_own_detail_target() -> None:
    rows = parse_student_grid(GRID_HTML)

    assert [r.student_id for r in rows] == ["STU-10000", "STU-10001"]
    assert rows[0].detail_target == "gvStudents$ctl02$lnkDetail"
    assert rows[1].detail_target == "gvStudents$ctl03$lnkDetail"


def test_parse_student_grid_skips_rows_without_a_detail_link() -> None:
    rows = parse_student_grid(GRID_HTML_WITH_SPURIOUS_ROW)


    assert [r.student_id for r in rows] == ["STU-10000", "STU-10001"]
    assert rows[0].detail_target == "gvStudents$ctl02$lnkDetail"
    assert rows[1].detail_target == "gvStudents$ctl04$lnkDetail"
