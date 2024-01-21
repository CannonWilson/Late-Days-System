"""
Test for pinging the database on Atlas, 
making sure it exists and is responsive.
"""

from ..db_utils import ping

def test_ping_mongo():
    assert ping() == "pong"