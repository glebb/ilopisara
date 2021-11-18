import os
from cachetools import cached, TTLCache
from dotenv import load_dotenv
import direct
import proxy

load_dotenv('../../.env')
USE_PROXY = bool(int(os.getenv('USE_PROXY')))
CLUB_ID = os.getenv('CLUB_ID')

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID):
    if USE_PROXY:
        return proxy.get_members(club_id)
    return direct.get_members(club_id)    

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(club_id=CLUB_ID, count=5):
    if USE_PROXY:
        return proxy.get_matches(club_id, count)    
    return direct.get_matches(club_id, count)    

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team):
    if USE_PROXY:
        return proxy.get_team_record(team)    
    return direct.get_team_record(team)    
