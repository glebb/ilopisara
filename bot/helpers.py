import os
import random
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

from extra import giphy

load_dotenv("../.env")
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = os.getenv("DISCORD_CHANNEL")

CLUB_ID = os.getenv("CLUB_ID")


class GAMETYPE(Enum):
    REGULARSEASON = "gameType5"
    PLAYOFFS = "gameType10"
    PRIVATE = "club_private"


goalie_fails = (
    "https://youtu.be/fR-_q9XeYZo?t=11",
    "https://www.youtube.com/watch?v=KFQnIFN1pYo",
    "https://youtu.be/e9civjk7z_M?t=179",
)


@dataclass
class ResultMark:
    mark: str
    gif: str


def chunk_using_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def is_win(match):
    scores = match["clubs"][os.getenv("CLUB_ID")]["scoreString"].split(" - ")
    return int(scores[0]) > int(scores[1])


def get_match_mark(match):
    if is_win(match):
        mark = ":white_check_mark: "
    else:
        mark = ":x: "
    return mark


def get_match_type_mark(match):
    mark = ""
    if match["gameType"] == GAMETYPE.REGULARSEASON.value:
        mark = " :hockey: "
    if match["gameType"] == GAMETYPE.PLAYOFFS.value:
        mark = " :trophy: "
    if match["gameType"] == GAMETYPE.PRIVATE.value:
        mark = " :handshake: "
    return mark


def teppo_scores(match):
    for _, p in match["players"][os.getenv("CLUB_ID")].items():
        if p["playername"] == "bodhi-FIN" and int(p["skgoals"]) > 0:
            return True
    return False


def is_goalie(match):
    for _, p in match["players"][os.getenv("CLUB_ID")].items():
        if p["position"] == "goalie":
            return True
    return False


def get_result_marks(match):
    if is_win(match):
        mark = ":white_check_mark: "
        gif = (
            "https://www.youtube.com/watch?v=IIlQgcTeHUE"
            if teppo_scores(match)
            else giphy.get_win()
        )
    else:
        mark = ":x:"
        gif = random.choice(goalie_fails) if is_goalie(match) else giphy.get_fail()
    return ResultMark(mark, gif)
