
from simplejson import JSONDecodeError
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib.parse
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}


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
    try:
        url = f"https://proclubs.ea.com/api/nhl/members/career/stats?platform={platform}&clubId={club_id}"
        data = http.get(url, timeout=4, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        print(err)
    return data
    
def get_matches(club_id, platform, count, game_type):
    data = []
    try:
        url = f"https://proclubs.ea.com/api/nhl/clubs/matches?matchType=gameType{str(game_type)}&matchType=gameType10&platform={platform}&clubIds={club_id}&maxResultCount={count}"
        data = http.get(url, timeout=4, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        print(err)
    return data

def get_team_record(team, platform):
    data = {}
    try:
        team_quoted = urllib.parse.quote(team)
        url = f"https://proclubs.ea.com/api/nhl/clubs/search?platform={platform}&clubName={team_quoted}"
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        print(err)
    return data