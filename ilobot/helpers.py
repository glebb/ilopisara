from dataclasses import dataclass
from enum import Enum

from ilobot.config import CLUB_ID
from ilobot.models import Match

PLATFORMS = {
    "common-gen5": "common-gen5",
    "ps5": "ps5",
    "xbsx": "xbox-series-xs",
    "common-gen4": "common-gen4",
    "ps4": "ps4",
    "xboxone": "xboxone",
}

POSITIONS = {
    "0": "Goalie",
    "1": "Right Defenseman",
    "2": "Left Defenseman",
    "3": "Right Wing",
    "4": "Left Wing",
    "5": "Center",
}

LOADOUTS = {
    "0": "Grinder",
    "1": "Playmaker",
    "2": "Sniper",
    "3": "Power Forward",
    "4": "Two-Way Forward",
    "5": "Enforcer",
    "6": "Dangler",
    "11": "Defensive Defenseman",
    "12": "Offensive Defenseman",
    "13": "Enforcer Defenseman",
    "14": "Two-Way Defenseman",
    "15": "Puck Moving Defenseman",
    "20": "Stand-Up",
    "21": "Hybrid",
    "22": "Butterfly",
    "100": "Hammer - Grinder",
    "101": "Surge - Playmaker",
    "106": "Vector - Dangler",
    "103": "Moonlight - Power FWD",
    "111": "Deepfreeze - DD",
    "115": "Bones - Puck Moving D",
    "120": "Wally - Stand-Up G",
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


def is_overtime(match: Match):
    return any(
        [int(player.toiseconds) > 3600 for player in match.players[CLUB_ID].values()]
    )


def get_match_mark(match: Match):
    if is_win(match):
        mark = (
            ":ballot_box_with_check: " if is_overtime(match) else ":white_check_mark: "
        )
    else:
        mark = ":alarm_clock: " if is_overtime(match) else ":x: "
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
