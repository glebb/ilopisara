from json.decoder import JSONDecodeError
import os
from cachetools import cached, TTLCache
from dotenv import load_dotenv
from data import proxy, direct
from enum import Enum

class GAMETYPE(Enum):
    REGULARSEASON = 5
    PLAYOFFS = 10

load_dotenv('../../.env')
USE_PROXY = bool(int(os.getenv('USE_PROXY')))
CLUB_ID = os.getenv('CLUB_ID')
PLATFORM = os.getenv('PLATFORM')

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID, platform=PLATFORM):
    try:
        if USE_PROXY:
            members = proxy.get_members(club_id, platform)
        else:
            members = direct.get_members(club_id, platform)
    except JSONDecodeError as err:
        print(err)
        members = {}
    return members

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(club_id=CLUB_ID, platform=PLATFORM, count=10, game_type = GAMETYPE.REGULARSEASON.value):
    try:
        if USE_PROXY:
            matches = proxy.get_matches(club_id, platform, count)    
        else:
            matches = direct.get_matches(club_id, platform, count, game_type)
    except JSONDecodeError as err:
        print(err)
        matches = []
    return matches

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team, platform=PLATFORM):
    if USE_PROXY:
        team_record = proxy.get_team_record(team, platform)    
    else:
        team_record = direct.get_team_record(team, platform)    
    return team_record
