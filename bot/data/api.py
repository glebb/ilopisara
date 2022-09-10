import os
from enum import Enum
from json.decoder import JSONDecodeError

from base_logger import logger
from cachetools import TTLCache, cached
from data import direct
from dotenv import load_dotenv


class GAMETYPE(Enum):
    REGULARSEASON = 5
    PLAYOFFS = 10


load_dotenv("../.env")
CLUB_ID = os.getenv("CLUB_ID")
PLATFORM = os.getenv("PLATFORM")


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID, platform=PLATFORM):
    members = {}
    try:
        members = direct.get_members(club_id, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return members


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(
    club_id=CLUB_ID, platform=PLATFORM, count=10, game_type=GAMETYPE.REGULARSEASON.value
):
    matches = []
    try:
        matches = direct.get_matches(club_id, platform, count, game_type)
    except JSONDecodeError as err:
        logger.error(err)
    return matches


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team, platform=PLATFORM):
    try:
        team_record = direct.get_team_record(team, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return team_record
