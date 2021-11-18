import os
from cachetools import cached, TTLCache
from dotenv import load_dotenv
from data import proxy, direct

load_dotenv('../../.env')
USE_PROXY = bool(int(os.getenv('USE_PROXY')))
CLUB_ID = os.getenv('CLUB_ID')
PLATFORM = os.getenv('PLATFORM')

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID, platform=PLATFORM):
    if USE_PROXY:
        return proxy.get_members(club_id)
    return direct.get_members(club_id, platform)    

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(club_id=CLUB_ID, platform=PLATFORM, count=5):
    if USE_PROXY:
        return proxy.get_matches(club_id, count)    
    return direct.get_matches(club_id, platform, count)

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team, platform=PLATFORM):
    if USE_PROXY:
        return proxy.get_team_record(team)    
    return direct.get_team_record(team, platform)    
