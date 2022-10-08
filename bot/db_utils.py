import copy

import helpers


def enrich_match(original_match, game_type):
    match = copy.deepcopy(original_match)
    match["gameType"] = game_type.value
    clubs = list(match["clubs"].keys())
    match["player_names"] = []
    match["opponent"] = {}
    for club in clubs:
        team_name = match["clubs"][club]["details"]["name"]
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
        if club != helpers.CLUB_ID:
            match["opponent"]["name"] = team_name
            match["opponent"]["id"] = club
    return match