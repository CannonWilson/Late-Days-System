"""
Tests for checking the backoff
update function. Should be able
to instantly update for just one student.
"""

from ..db_utils import update_ld_test_version

def test_backoff_update():
    netid = "kgwilson2"
    project_num = 2
    ld_used = 3
    expected_result = {'2' : 3}
    assert update_ld_test_version(netid, project_num, ld_used) == expected_result
