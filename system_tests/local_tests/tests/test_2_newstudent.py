"""
Test for insering a new document for a 
new student into the students collection
"""

from ..db_utils import insert_new_student

def test_new_student():
    new_netid = "kgwilson2"
    assert insert_new_student(new_netid, delete_existing=True) == True