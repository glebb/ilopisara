
import requests
import os
from cachetools import cached, TTLCache
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib.parse
from dotenv import load_dotenv
load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"],
    backoff_factor=0.2
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_members(club_id=CLUB_ID):
    print("get_members")
    data = {}
    try:
        data = http.get('http://localhost:3000/members/'+club_id, timeout=4).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data
    

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches(club_id=CLUB_ID):
    print("get_matches")
    data = {}
    try:
        data = http.get('http://localhost:3000/matches/' + club_id, timeout=4).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_team_record(team):
    print("get_team_record :" + team)
    data = {}
    try:
        data = http.get('http://localhost:3000/team/' + urllib.parse.quote(team), timeout=10).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data
