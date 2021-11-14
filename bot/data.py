
import requests
import os
from cachetools import cached, TTLCache
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib.parse
from dotenv import load_dotenv
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}

load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')
PLATFORM = os.getenv('PLATFORM')
USE_PROXY = bool(int(os.getenv('USE_PROXY')))

#Season stats: https://proclubs.ea.com/api/nhl/clubs/seasonalStats?platform=ps4&clubIds=19963

retry_strategy = Retry(
    total=2,
    backoff_factor=0.2
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)
http.get('https://www.ea.com/fi-fi/games/nhl/nhl-22/pro-clubs/overview?clubId=19963&platform=ps4')

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID):
    print("get_members")
    data = {}
    try:
        if USE_PROXY:
            url = 'http://localhost:3000/members/'+club_id
        else:
            url = f"https://proclubs.ea.com/api/nhl/members/career/stats?platform={PLATFORM}&clubId={club_id}"
        data = http.get(url, timeout=4, headers=headers).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data
    

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(club_id=CLUB_ID):
    print("get_matches")
    data = {}
    try:
        if USE_PROXY:
            url = 'http://localhost:3000/matches/' + club_id
        else:
            url = f"https://proclubs.ea.com/api/nhl/clubs/matches?matchType=gameType5&platform={PLATFORM}&clubIds={club_id}"
        data = http.get(url, timeout=4, headers=headers).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team):
    return None #disabled for now
    print("get_team_record :" + team)
    data = {}
    try:
        team_quoted = urllib.parse.quote(team)
        if USE_PROXY:
            url = 'http://localhost:3000/team/' + team_quoted
        else:
            url = f"https://proclubs.ea.com/api/nhl/clubs/search?platform={PLATFORM}&clubName={team_quoted}"
        data = http.get(url, timeout=10, headers=headers).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data

if __name__ == '__main__':
    print(get_members())