# pylint: disable=C0413
import os
import sys
from typing import List, Literal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from dacite import from_dict

from ilobot import db_utils
from ilobot.base_logger import logger
from ilobot.data import api
from ilobot.helpers import GAMETYPE
from ilobot.models import Match

PLATFORM = "common-gen5"
CLUB_ID = "2"


@pytest.mark.parametrize("count", [(1)])
def test_get_matches(count: Literal[1]):
    matches = api.get_matches(CLUB_ID, PLATFORM, count, GAMETYPE.REGULARSEASON.value)
    assert len(matches) == count
    assert isinstance(matches, List) is True
    match = db_utils.enrich_match(matches[0], GAMETYPE.REGULARSEASON)
    from_dict(data_class=Match, data=match)


def test_get_matches_max_result_count_capped_to_5():
    matches = api.get_matches(CLUB_ID, PLATFORM, 20)
    assert len(matches) <= 5


@pytest.mark.parametrize("clubId", [(""), ("00006660000"), ("cxvcxvcxvc"), None])
def test_get_matches_wrong_id(clubId: Literal['', '00006660000', 'cxvcxvcxvc'] | None):
    matches = api.get_matches(clubId, PLATFORM)
    assert len(matches) == 0
    assert isinstance(matches, List) is True


def test_get_members():
    members = api.get_members(CLUB_ID, PLATFORM)
    assert len(members) > 1
    assert isinstance(members, List) is True


@pytest.mark.parametrize("club_id", [(""), ("00006660000"), ("cxvcxvcxvc"), None])
def test_get_members_wrong_id(club_id: Literal['', '00006660000', 'cxvcxvcxvc'] | None):
    members = api.get_members(club_id, PLATFORM)
    assert len(members) == 0
    assert isinstance(members, List) is True


def test_get_team_record():
    record = api.get_team_record("Nighthawks", PLATFORM)
    assert len(record) == 1
    assert isinstance(record, dict) is True


def test_get_team_record_unknown_team():
    record = api.get_team_record("poiuerew slfdsj vmxcnvxc", PLATFORM)
    assert len(record) == 0
    assert isinstance(record, dict) is True


def test_team_info():
    info = api.get_team_info(CLUB_ID, PLATFORM)
    assert len(info) == 1
    assert isinstance(info, dict) is True


def test_seasonal_stats():
    stats = api.get_seasonal_stats(CLUB_ID, PLATFORM)
    assert len(stats) == 1
    assert isinstance(stats, List) is True


def test_get_member():
    member = api.get_member("InThaSky", PLATFORM)
    assert member["name"] == "InThaSky"
