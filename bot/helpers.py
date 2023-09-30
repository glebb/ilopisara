import os
import random
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv
from extra import giphy
from models import Match

load_dotenv("../.env")
CLUB_ID = os.getenv("CLUB_ID")
PLATFORM = os.getenv("PLATFORM")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL"))
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
OAUTH = os.getenv("TWITCH_OAUTH")
STREAMERS = os.getenv("TWITCH_STREAMERS")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")

PLATFORMS = {
    "common-gen5": "common-gen5",
    "ps5": "ps5",
    "xbsx": "xbox-series-xs",
    "ps4": "ps4",
    "xboxone": "xboxone",
}


class GAMETYPE(Enum):
    REGULARSEASON = "gameType5"
    PLAYOFFS = "gameType10"
    # PRIVATE = "club_private"


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


def is_win(match: Match):
    return match.win


def get_match_mark(match):
    if is_win(match):
        mark = ":white_check_mark: "
    else:
        mark = ":x: "
    return mark


def get_match_type_mark(match: Match):
    mark = ""
    if match.gameType == GAMETYPE.REGULARSEASON.value:
        mark = " :hockey: "
    if match.gameType == GAMETYPE.PLAYOFFS.value:
        mark = " :trophy: "
    # if match.gameType == GAMETYPE.PRIVATE.value:
    #    mark = " :handshake: "
    return mark


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
            else giphy.get_win()
        )
    else:
        mark = ":x:"
        gif = random.choice(goalie_fails) if is_goalie(match) else giphy.get_fail()
    return ResultMark(mark, gif)


def get_platform(match: Match):
    opponent_id = match.clubs[CLUB_ID].opponentClubId
    return list(match.players[opponent_id].values())[0].clientPlatform or "ps5"


def get_vs_players(match: Match):
    opponent_id = match.clubs[CLUB_ID].opponentClubId
    players = map(lambda x: x.playername, match.players[opponent_id].values())
    return ", ".join(list(players))
