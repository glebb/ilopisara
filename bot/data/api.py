import os
from functools import cache
from json.decoder import JSONDecodeError

import helpers
from base_logger import logger
from cachetools import TTLCache, cached
from data import direct
from dotenv import load_dotenv

load_dotenv("../.env")
CLUB_ID = os.getenv("CLUB_ID")
PLATFORM = os.getenv("PLATFORM")


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID, platform=PLATFORM):
    data = {}
    try:
        data = direct.get_members(club_id, platform)
    except JSONDecodeError as err:
        logger.error(err)
    if data:
        return data["members"]
    return []


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(
    club_id=CLUB_ID,
    platform=PLATFORM,
    count=10,
    game_type=helpers.GAMETYPE.REGULARSEASON.value,
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


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_info(team, platform=PLATFORM):
    try:
        team_info = direct.get_team_info(team, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return team_info


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_seasonal_stats(team, platform=PLATFORM):
    try:
        stats = direct.get_seasonal_stats(team, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return stats


@cache
def get_member(member_name, platform=PLATFORM):
    data = {}
    try:
        data = direct.get_member(member_name, platform)
    except JSONDecodeError as err:
        logger.error(err)
    if data:
        return data["members"][0]
    return None
