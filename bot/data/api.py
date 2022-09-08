import os
from enum import Enum
from json.decoder import JSONDecodeError

from cachetools import TTLCache, cached
from data import direct, proxy
from dotenv import load_dotenv


class GAMETYPE(Enum):
    REGULARSEASON = 5
    PLAYOFFS = 10

load_dotenv('../../.env')
USE_PROXY = bool(int(os.getenv('USE_PROXY')))
CLUB_ID = os.getenv('CLUB_ID')
PLATFORM = os.getenv('PLATFORM')

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID, platform=PLATFORM):
    members = {}
    try:
        if USE_PROXY:
            members = proxy.get_members(club_id, platform)
        else:
            members = direct.get_members(club_id, platform)
    except JSONDecodeError as err:
        print(err)        
    return members

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(club_id=CLUB_ID, platform=PLATFORM, count=10, game_type = GAMETYPE.REGULARSEASON.value):
    matches = []
    try:
        if USE_PROXY:
            matches = proxy.get_matches(club_id, platform, count)    
        else:
            matches = direct.get_matches(club_id, platform, count, game_type)
    except JSONDecodeError as err:
        print(err)        
    return matches

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team, platform=PLATFORM):
    team_record = direct.get_team_record(team, platform)    
    return team_record
