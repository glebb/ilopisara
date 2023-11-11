from functools import cache
from json.decoder import JSONDecodeError

from cachetools import TTLCache, cached

import ilobot.config
import ilobot.helpers as helpers
from ilobot.base_logger import logger
from ilobot.data import direct


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=ilobot.config.CLUB_ID, platform=ilobot.config.PLATFORM):
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
    club_id=ilobot.config.CLUB_ID,
    platform=ilobot.config.PLATFORM,
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
def get_team_record(team, platform=ilobot.config.PLATFORM):
    try:
        team_record = direct.get_team_record(team, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return team_record


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_info(team, platform=ilobot.config.PLATFORM):
    try:
        team_info = direct.get_team_info(team, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return team_info


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_seasonal_stats(team, platform=ilobot.config.PLATFORM):
    try:
        stats = direct.get_seasonal_stats(team, platform)
    except JSONDecodeError as err:
        logger.error(err)
    return stats


@cache
def get_member(member_name, platform=ilobot.config.PLATFORM):
    data = {}
    try:
        data = direct.get_member(member_name, platform)
    except JSONDecodeError as err:
        logger.error(err)
    if data:
        return data["members"][0]
    return None
