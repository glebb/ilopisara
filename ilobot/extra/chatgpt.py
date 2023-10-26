import json

import openai
from openai.error import RateLimitError, ServiceUnavailableError

from ilobot.base_logger import logger
from ilobot.data import api
from ilobot.helpers import CLUB_ID, GPT_MODEL, OPEN_API
from ilobot.jsonmap import match

openai.api_key = OPEN_API

skip_keys = [
    "matchId",
    "timeAgo",
    "aggregate",
    "player_names",
    "toi",
    "toa",
    "raw",
    "teamArtAbbr",
    "opponentTeamArtAbbr",
    "toiseconds",
    "dnf",
    "passc",
    "passa",
    "customKit",
    "teamId",
    "opponentTeamId",
    "OnlineGameType",
    "asset",
    "rank",
    "class",
    "gameType",
    "clubDivision",
    "memberString",
    "posSorted",
    "timestamp",
    "opponent",
    "playerLevel",
    "skfow",
    "skfol",
    "skshotpct",
]

skip_just_player_keys = [
    "removedReason",
    "result",
    "score",
    "scoreRaw",
    "scoreString",
    "teamSide",
]

# Fixed mappings for key name conversions
key_mappings = {
    "opponentClubId": "Opponent Club ID",
    "opponentTeamArtAbbr": "Opponent Team abbreviation",
    "teamArtAbbr": "Team abbreviation",
    "name": "Club name",
    "ppo": "Power-play opportunities",
}


# Function to convert key names using fixed mappings
def convert_keys(temp):
    converted_data = {}
    for key, value in temp.items():
        xxx = key
        for skip_key in skip_keys:
            if skip_key in key:
                xxx = None
        if not xxx:
            continue
        if key.startswith("sk"):
            if temp["position"] == "goalie":
                continue
        if key.startswith("skfo") and temp["position"] != "center":
            continue
        if key.startswith("gl"):
            if temp["position"] != "goalie":
                continue
        if "position" in temp:
            if key in skip_just_player_keys:
                continue
            if int(temp["skgiveaways"]) < 5:
                continue

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            converted_data[xxx] = convert_keys(value)
        elif key in key_mappings:
            # If key is in the mappings, replace it with the full name
            converted_data[key_mappings[key]] = value
        elif key in match:
            # If key is in the mappings, replace it with the full name
            converted_data[match[key]] = value
        else:
            converted_data[key] = value
    return converted_data


def clean_up_data(game: dict):
    converted_data = convert_keys(game)
    for key in converted_data["clubs"].keys():
        if key == str(CLUB_ID):
            converted_data["clubs"][key]["players"] = converted_data["players"][key]
        else:
            converted_data["clubs"][key]["players"] = {}

    clubs = {}
    for club_id, club_data in converted_data["clubs"].items():
        club_name = club_data["details"]["Club name"]
        clubs[club_name] = club_data
        clubs[club_name]["clubId"] = club_id
        del clubs[club_name]["details"]
        clubs[club_name]["players"] = {
            api.get_member(player_data["playername"])["skplayername"]
            if "skplayername" in api.get_member(player_data["playername"])
            else player_data["playername"]: player_data
            for player_id, player_data in club_data["players"].items()
        }
        for player in clubs[club_name]["players"]:
            clubs[club_name]["players"][player]["playername"] = player
    del converted_data["players"]
    converted_data["clubs"] = clubs
    return converted_data


def check_dnf(game: dict):
    for club in game["clubs"]:
        if (
            game["clubs"][club]["winnerByDnf"] != "0"
            or game["clubs"][club]["winnerByGoalieDnf"] != "0"
        ):
            return True
    return False


async def write_gpt_summary(game: dict, history=None):
    our_team = game["clubs"][CLUB_ID]["details"]["name"]
    cleaned_game = clean_up_data(game)
    json_output = json.dumps(cleaned_game)
    history_json_output = json.dumps({"previous_games": history})
    messages = [
        {
            "role": "system",
            "content": f"You are a Yoosef, entitled general manager of hockey club {our_team}."
            "You are mean, point out the mistakes players make and give praise only on "
            "most exceptional performances.",
        },
        {
            "role": "user",
            "content": "Analyze the hockey game that just took place, based on following "
            "json data and imaginary events. Critique the performance of your team and your "
            "players. Throw insults if needed to make a point. ",
        },
    ]
    if (
        game["clubs"][CLUB_ID]["losses"] != "0"
        and int(game["clubs"][CLUB_ID]["shots"]) < 20
    ):
        messages.append(
            {
                "role": "user",
                "content": "Comment the poor shots statistics with a phrase 'VETOJA HYVÄT HERRAT!'",
            }
        )

    messages.append({"role": "user", "content": "\n###\n" + json_output + "\n"})
    messages.append({"role": "user", "content": "\n###\n" + history_json_output + "\n"})

    if check_dnf(cleaned_game):
        messages.append(
            {
                "role": "user",
                "content": "If the data indicates 'winnerByDnf' or 'winnerByGoalieDnf' "
                "with other than value 0, make a big deal about the other team chickening out by not "
                "finishing the game properly. Don't mention the data keys or values as such. "
                f"If it was the opponent who won by {our_team} not finishing the team, raise hell.",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": "The team cowardly quit the game before it was finished.",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": "The team demonstrated despicable attitude by quitting the match until it was finished.",
            }
        )
    messages.append(
        {"role": "user", "content": "Limit the reply to 290 words maximum."}
    )

    try:
        chat_completion = await openai.ChatCompletion.acreate(
            model=GPT_MODEL,
            messages=messages,
            temperature=1.33,
            top_p=0.5,
            frequency_penalty=0.3,
            presence_penalty=1,
        )
    except (ServiceUnavailableError, RateLimitError):
        logger.exception("OPENAI error")
        return None

    return chat_completion["choices"][0]["message"]["content"]
