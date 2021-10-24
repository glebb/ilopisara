
import requests
from cachetools import cached, TTLCache

@cached(cache=TTLCache(maxsize=1024, ttl=240))
def get_members():
    print("get_members")
    data = {}
    try:
        data = requests.get('http://localhost:3000/members', timeout=6).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data
    

@cached(cache=TTLCache(maxsize=1024, ttl=240))
def get_matches():
    print("get_matches")
    data = {}
    try:
        data =requests.get('http://localhost:3000/matches', timeout=6).json()
    except requests.exceptions.Timeout as err:
        print(err)
    return data