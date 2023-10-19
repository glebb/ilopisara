import os
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

from ilobot.models import Match

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
load_dotenv(f"{__location__}/../.env")
DB_NAME = os.getenv("DB_NAME")
API_KEY = os.getenv("GIPHY_API_KEY")
OPEN_API = os.getenv("OPEN_API")
DEBUG = int(os.getenv("DEBUG"))
CLUB_ID = os.getenv("CLUB_ID")
PLATFORM = os.getenv("PLATFORM")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL"))
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
OAUTH = os.getenv("TWITCH_OAUTH")
STREAMERS = os.getenv("TWITCH_STREAMERS")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
TUMBLR_KEY = os.getenv("TUMBLR_KEY")
TUMBLR_SECRET = os.getenv("TUMBLR_SECRET")
TUMBLR_OAUTH_KEY = os.getenv("TUMBLR_OAUTH_KEY")
TUMBLR_OAUTH_SECRET = os.getenv("TUMBLR_OAUTH_SECRET")

PLATFORMS = {
    "common-gen5": "common-gen5",
    "ps5": "ps5",
    "xbsx": "xbox-series-xs",
    "common-gen4": "common-gen4",
    "ps4": "ps4",
    "xboxone": "xboxone",
}


class GAMETYPE(Enum):
    REGULARSEASON = "gameType5"
    PLAYOFFS = "gameType10"
    # PRIVATE = "club_private"


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


def get_platform(match: Match):
    opponent_id = match.clubs[CLUB_ID].opponentClubId
    return list(match.players[opponent_id].values())[0].clientPlatform or "ps5"


def get_vs_players(match: Match):
    opponent_id = match.clubs[CLUB_ID].opponentClubId
    players = map(lambda x: x.playername, match.players[opponent_id].values())
    return ", ".join(list(players))
