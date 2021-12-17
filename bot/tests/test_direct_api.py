import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data import api
api.USE_PROXY = False

PLATFORM= 'ps4'
CLUB_ID = '19963'


@pytest.mark.parametrize("count", [(1), (5)])
def test_get_matches(count):
    matches = api.get_matches(CLUB_ID, PLATFORM, count)
    assert len(matches) == count
    assert type(matches) == type([])

def test_get_matches_max_result_count_capped_to_5():
    matches = api.get_matches(CLUB_ID, PLATFORM, 20)
    assert len(matches) == 5

@pytest.mark.parametrize("clubId", [(""), ("00006660000"), ("cxvcxvcxvc"), None])
def test_get_matches_wrong_id(clubId):
    matches = api.get_matches(clubId, PLATFORM)
    assert len(matches) == 0
    assert type(matches) == type([])

def test_get_members():
    members = api.get_members(CLUB_ID, PLATFORM)
    assert len(members) > 1
    assert type(members) == type({})

@pytest.mark.parametrize("clubId", [(""), ("00006660000"), ("cxvcxvcxvc"), None])
def test_get_members_wrong_id(clubId):
    members = api.get_members(clubId, PLATFORM)
    assert len(members) == 0
    assert type(members) == type({})    

def test_get_team_record():
    record = api.get_team_record("Ilo Pisara")
    assert len(record) == 1
    assert type(record) == type({}) 

def test_get_team_record_unknown_team():
    record = api.get_team_record("poiuerew slfdsj vmxcnvxc")
    assert len(record) == 0
    assert type(record) == type({})