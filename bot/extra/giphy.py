import os
import random

import requests
from dotenv import load_dotenv

load_dotenv('../.env')
API_KEY = os.getenv('GIPHY_API_KEY')
url = "http://api.giphy.com/v1/gifs/search"

params = [
    ["q", "hockey fail"],
    ("api_key", API_KEY),
    ("limit", "100"),
    ("rating", "r")
]

response = requests.get(url, params=params)
fails = response.json()
params[0][1] = "hockey win"
response = requests.get(url, params=params)
wins = response.json()

def get_win():
    win = random.choice(wins['data'])
    if win:
        return win['images']['original']['url']

def get_fail():
    fail = random.choice(fails['data'])
    if fail:
        return fail['images']['original']['url']

