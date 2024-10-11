import copy

from ilobot import config
from ilobot.base_logger import logger


def _is_win(match, club_id=None):
    scores = match["clubs"][config.CLUB_ID if not club_id else club_id][
        "scoreString"
    ].split(" - ")
    return int(scores[0]) > int(scores[1])


def enrich_match(original_match, game_type, club_id=None):
    club_id = club_id or config.CLUB_ID
    match = copy.deepcopy(original_match)
    match["gameType"] = game_type.value
    match["win"] = _is_win(match, club_id)
    clubs = list(match["clubs"].keys())
    match["player_names"] = []
    match["opponent"] = {}
    for club in clubs:
        if (
            "details" in match["clubs"][club]
            and "name" in match["clubs"][club]["details"]
        ):
            team_name = match["clubs"][club]["details"]["name"]
        else:
            team_name = "UNKNOWN"
            logger.error(f"Team name not found for {club} in match {match['matchId']}")
        player_ids = list(match["players"][club].keys())
        for player in player_ids:
            match["players"][club][player]["skpoints"] = int(
                match["players"][club][player]["skgoals"]
            ) + int(match["players"][club][player]["skassists"])
            temp = {}
            temp["name"] = match["players"][club][player]["playername"]
            temp["id"] = player
            temp["club_id"] = club
            temp["club_name"] = team_name
            match["player_names"].append(temp)
        if club != club_id:
            match["opponent"]["name"] = team_name
            match["opponent"]["id"] = club
    return match
