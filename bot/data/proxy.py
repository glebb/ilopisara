
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib.parse
from dotenv import load_dotenv
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}

load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')
PLATFORM = os.getenv('PLATFORM')
USE_PROXY = bool(int(os.getenv('USE_PROXY')))

# https://proclubs.ea.com/api/nhl/clubs/matches?platform=ps4&clubIds=19963&matchType=gameType5&maxResultCount=50
#Season stats: https://proclubs.ea.com/api/nhl/clubs/seasonalStats?platform=ps4&clubIds=19963

retry_strategy = Retry(
    total=2,
    backoff_factor=0.2
)

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)
def get_members(club_id, platform):
    data = {}
    params = {'platform': platform}
    try:
        url = 'http://localhost:3000/members/'+club_id
        data = http.get(url, timeout=4, headers=headers, params=params).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data
    
def get_matches(club_id, platform, count):
    data = {}
    params = {'platform': platform, 'count': count}
    try:
        url = 'http://localhost:3000/matches/' + club_id
        data = http.get(url, timeout=4, headers=headers, params=params).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data

def get_team_record(team, platform):
    data = {}
    params = {'platform': platform}
    try:
        team_quoted = urllib.parse.quote(team)
        url = 'http://localhost:3000/team/' + team_quoted
        data = http.get(url, timeout=10, headers=headers, params=params).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data