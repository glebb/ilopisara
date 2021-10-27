
import requests
from cachetools import cached, TTLCache
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

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
def get_members():
    print("get_members")
    data = {}
    try:
        data = http.get('http://localhost:3000/members', timeout=4).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data
    

@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_matches():
    print("get_matches")
    data = {}
    try:
        data = http.get('http://localhost:3000/matches', timeout=4).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data