import random

import requests

from ilobot.config import API_KEY, CLUB_ID
from ilobot.helpers import ResultMark, is_win

goalie_fails = (
    "https://youtu.be/fR-_q9XeYZo?t=11",
    "https://www.youtube.com/watch?v=KFQnIFN1pYo",
    "https://youtu.be/e9civjk7z_M?t=179",
)


URL = "http://api.giphy.com/v1/gifs/search"

params = [("q", "hockey fail"), ("api_key", API_KEY), ("limit", "100"), ("rating", "r")]

response = requests.get(URL, params=params, timeout=5)
fails = response.json()
params[0] = ("q", "hockey win")
response = requests.get(URL, params=params, timeout=5)
wins = response.json()


def get_win():
    win = random.choice(wins["data"])
    if win:
        return win["images"]["original"]["url"]


def get_fail():
    fail = random.choice(fails["data"])
    if fail:
        return fail["images"]["original"]["url"]


def teppo_scores(match):
    for _, p in match["players"][CLUB_ID].items():
        if p["playername"] == "bodhi-FIN" and int(p["skgoals"]) > 0:
            return True
    return False


def is_goalie(match):
    for _, p in match["players"][CLUB_ID].items():
        if p["position"] == "goalie":
            return True
    return False


def get_result_marks(match):
    if is_win(match):
        mark = ":white_check_mark: "
        gif = (
            "https://www.youtube.com/watch?v=IIlQgcTeHUE"
            if teppo_scores(match)
            else get_win()
        )
    else:
        mark = ":x:"
        gif = random.choice(goalie_fails) if is_goalie(match) else get_fail()
    return ResultMark(mark, gif)
